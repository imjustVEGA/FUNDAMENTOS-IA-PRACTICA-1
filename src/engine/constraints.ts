import type { Scenario, Point, Zone } from '../types';
import { angularDistanceDeg, uniformPoint } from './geometry';
import type { PRNG } from './prng';

function extractLatLon(p: Point | [number, number]): [number, number] {
  if (Array.isArray(p)) return [p[0], p[1]];
  return [p.lat, p.lon];
}

export function isValidPoint(
  point: Point | [number, number],
  scenario: Scenario,
): boolean {
  const [lat, lon] = extractLatLon(point);
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) return false;
  if (lat < -90.0 || lat > 90.0 || lon < -180.0 || lon > 180.0) return false;

  const activeZones = scenario.zones.filter((z) => z.active);
  for (const z of activeZones) {
    const dist = angularDistanceDeg(lat, lon, z.lat, z.lon);
    if (dist <= z.radius_deg + 1e-9) {
      return false;
    }
  }
  return true;
}

export function detectViolations(
  coords: (Point | [number, number])[],
  scenario: Scenario,
): string[] {
  const issues: string[] = [];
  const activeZones = scenario.zones.filter((z) => z.active);
  if (!activeZones.length) return issues;

  coords.forEach((coord, idx) => {
    const [lat, lon] = extractLatLon(coord);
    for (const z of activeZones) {
      const dist = angularDistanceDeg(lat, lon, z.lat, z.lon);
      if (dist <= z.radius_deg + 1e-9) {
        issues.push(`S${idx + 1}: ${z.name}`);
      }
    }
  });

  return issues;
}

export function repararSatelite(
  point: [number, number],
  scenario: Scenario,
  rng: PRNG,
  maxAttempts: number = 300,
): [number, number] | null {
  if (isValidPoint(point, scenario)) {
    return [point[0], point[1]];
  }

  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const candidate = uniformPoint(rng);
    if (isValidPoint(candidate, scenario)) {
      return candidate;
    }
  }

  return null;
}

export function repararConfiguracion(
  coords: [number, number][],
  scenario: Scenario,
  rng: PRNG,
  maxAttempts: number = 300,
): [number, number][] | null {
  const repaired: [number, number][] = [];
  for (let i = 0; i < coords.length; i++) {
    const sat = repararSatelite(coords[i], scenario, rng, maxAttempts);
    if (sat === null) return null;
    repaired.push(sat);
  }
  return repaired;
}
