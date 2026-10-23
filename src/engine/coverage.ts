import type { Scenario, Point, Evaluation, Coverage } from '../types';
import {
  R_TIERRA_KM,
  vectorFromCoord,
  diskSamples,
  dot3,
  angularDistanceDeg,
  type Vec3,
} from './geometry';
import { detectViolations } from './constraints';

export class Evaluator {
  private scenario: Scenario;
  /** Para cada una de las regiones, array de muestras como vectores 3D unitarios */
  private regionSampleVectors: Vec3[][];
  private totalWeight: number;

  constructor(scenario: Scenario) {
    this.scenario = scenario;
    const sampleCount = scenario.samples || 128;
    this.regionSampleVectors = scenario.regions.map((r) => {
      const radiusKm = r.radius_km ?? 300.0;
      const samples = diskSamples(r.lat, r.lon, radiusKm, sampleCount);
      return samples.map(([sLat, sLon]) => vectorFromCoord(sLat, sLon));
    });
    this.totalWeight = scenario.regions.reduce((acc, r) => acc + (r.weight > 0 ? r.weight : 1.0), 0);
  }

  evaluate(coords: (Point | [number, number])[]): Evaluation {
    const latLons: [number, number][] = coords.map((c) =>
      Array.isArray(c) ? [c[0], c[1]] : [c.lat, c.lon],
    );

    const satVectors: Vec3[] = latLons.map(([lat, lon]) =>
      vectorFromCoord(lat, lon),
    );

    const footprintKm = this.scenario.footprint_km ?? 650.0;
    const cosThreshold = Math.cos(footprintKm / R_TIERRA_KM) - 1e-12;

    const coverageList: Coverage[] = [];
    let weightedCoverageSum = 0;
    let weightedCoveredRegionsSum = 0;
    let coveredRegionsCount = 0;

    for (let rIdx = 0; rIdx < this.scenario.regions.length; rIdx++) {
      const region = this.scenario.regions[rIdx];
      const samples = this.regionSampleVectors[rIdx];
      let coveredSamples = 0;

      for (let sIdx = 0; sIdx < samples.length; sIdx++) {
        const sVec = samples[sIdx];
        let maxDot = -1;
        for (let satIdx = 0; satIdx < satVectors.length; satIdx++) {
          const d = dot3(sVec, satVectors[satIdx]);
          if (d > maxDot) maxDot = d;
        }
        if (maxDot >= cosThreshold) {
          coveredSamples++;
        }
      }

      const fraction = samples.length > 0 ? coveredSamples / samples.length : 0;
      const isCovered = fraction >= 0.8;
      if (isCovered) coveredRegionsCount++;

      const w = region.weight > 0 ? region.weight : 1.0;
      weightedCoverageSum += w * fraction;
      if (isCovered) weightedCoveredRegionsSum += w;

      coverageList.push({
        name: region.name,
        fraction,
        covered: isCovered,
        weight: region.weight,
      });
    }

    const issues = detectViolations(latLons, this.scenario);
    const isValid = issues.length === 0;

    const weightedCoverage = this.totalWeight > 0 ? weightedCoverageSum / this.totalWeight : 0;
    const weightedCoveredRegions = this.totalWeight > 0 ? weightedCoveredRegionsSum / this.totalWeight : 0;
    const rawFitness = 100.0 * (0.8 * weightedCoverage + 0.2 * weightedCoveredRegions);
    const fitness = isValid ? Math.max(0.0, Math.min(100.0, rawFitness)) : 0.0;

    let minSeparation = 180.0;
    for (let i = 0; i < latLons.length; i++) {
      for (let j = i + 1; j < latLons.length; j++) {
        const sep = angularDistanceDeg(latLons[i][0], latLons[i][1], latLons[j][0], latLons[j][1]);
        if (sep < minSeparation) minSeparation = sep;
      }
    }

    const allCovered = coveredRegionsCount === this.scenario.regions.length;
    const status: Evaluation['status'] = !isValid
      ? 'invalid'
      : allCovered
        ? 'valid'
        : 'valid_insufficient';

    return {
      valid: isValid,
      status,
      fitness,
      covered_regions: coveredRegionsCount,
      coverage: coverageList,
      violations: issues,
      separation_deg: latLons.length > 1 ? minSeparation : 0.0,
    };
  }
}
