import type { Scenario, Parameters, Point, Run, Generation, Evaluation } from '../types';
import { PRNG } from './prng';
import { uniformPoint, move } from './geometry';
import { Evaluator } from './coverage';
import { repararConfiguracion } from './constraints';

function toPoints(coords: [number, number][]): Point[] {
  return coords.map(([lat, lon]) => ({ lat: Number(lat), lon: Number(lon) }));
}

function cloneCoords(coords: [number, number][]): [number, number][] {
  return coords.map((c) => [c[0], c[1]]);
}

export function optimize(scenario: Scenario, p: Parameters): Run {
  const rng = new PRNG(p.seed);
  const evaluator = new Evaluator(scenario);

  const result: Run = {
    status: 'no_feasible_found',
    message: 'No se encontró una configuración factible dentro del presupuesto; no demuestra imposibilidad.',
    seed: p.seed,
    parameters: p,
    scenario,
    history: [],
  };

  // Restricción matemática de 180°
  if (scenario.zones.some((z) => z.active && z.radius_deg >= 180.0)) {
    result.message = 'Una zona activa de 180° excluye toda la esfera: escenario imposible en este modelo.';
    return result;
  }

  const repair = (c: [number, number][]): [number, number][] | null => {
    return repararConfiguracion(c, scenario, rng, p.attempts);
  };

  let population: [number, number][][] = [];

  for (let index = 0; index < p.population; index++) {
    let c: [number, number][] = Array.from({ length: 8 }, () => uniformPoint(rng));
    if (index > 0 && index % 2 === 1) {
      for (let j = 0; j < 8; j++) {
        const r = scenario.regions[rng.integers(scenario.regions.length)];
        c[j] = move([r.lat, r.lon], rng.normal(0, 9), rng.normal(0, 9));
      }
    }
    const repaired = repair(c);
    if (!repaired) {
      return result;
    }
    population.push(repaired);
  }

  result.initial = toPoints(population[0]);
  result.initial_evaluation = evaluator.evaluate(population[0]);

  let evaluations: Evaluation[] = population.map((c) => evaluator.evaluate(c));

  const compareFitness = (idxA: number, idxB: number): number => {
    const diff = evaluations[idxB].fitness - evaluations[idxA].fitness;
    if (Math.abs(diff) > 1e-7) return diff;
    return evaluations[idxB].separation_deg - evaluations[idxA].separation_deg;
  };

  const getBestIndex = (): number => {
    let best = 0;
    for (let i = 1; i < p.population; i++) {
      if (compareFitness(best, i) < 0) {
        best = i;
      }
    }
    return best;
  };

  const record = (gen: number) => {
    const bestIdx = getBestIndex();
    const scores = evaluations.map((e) => e.fitness);
    const sum = scores.reduce((a, b) => a + b, 0);
    const mean = scores.length > 0 ? sum / scores.length : 0;
    const bestScore = Math.max(...scores);
    const worstScore = Math.min(...scores);
    const validCount = evaluations.filter((e) => e.valid).length;

    result.history.push({
      generation: gen,
      best: Number(bestScore.toFixed(3)),
      mean: Number(mean.toFixed(3)),
      worst: Number(worstScore.toFixed(3)),
      valid_count: validCount,
      best_configuration: toPoints(population[bestIdx]),
      covered_regions: evaluations[bestIdx].covered_regions,
    });
  };

  record(0);

  for (let generation = 1; generation <= p.generations; generation++) {
    const order = Array.from({ length: p.population }, (_, i) => i).sort((a, b) =>
      compareFitness(a, b),
    );

    const children: [number, number][][] = order
      .slice(0, p.elite)
      .map((i) => cloneCoords(population[i]));

    const tournament = (): [number, number][] => {
      const ids = rng.choice(p.population, p.tournament);
      let bestChoice = ids[0];
      for (let k = 1; k < ids.length; k++) {
        if (compareFitness(bestChoice, ids[k]) < 0) {
          bestChoice = ids[k];
        }
      }
      return population[bestChoice];
    };

    const maxTries = (p.population - p.elite) * 3;
    for (let attempt = 0; attempt < maxTries; attempt++) {
      if (children.length >= p.population) break;
      const parentA = tournament();
      const parentB = tournament();
      const child: [number, number][] = cloneCoords(parentA);

      if (rng.random() < p.crossover) {
        for (let sIdx = 0; sIdx < 8; sIdx++) {
          if (rng.random() < 0.5) {
            child[sIdx] = [parentB[sIdx][0], parentB[sIdx][1]];
          }
        }
      }

      for (let j = 0; j < 8; j++) {
        if (rng.random() < p.mutation) {
          child[j] = rng.random() < 0.15
            ? uniformPoint(rng)
            : move(child[j], rng.normal(0, 5), rng.normal(0, 5));
        }
      }

      const repairedChild = repair(child);
      if (repairedChild) {
        children.push(repairedChild);
      }
    }

    // Respaldo si no se alcanzaron suficientes hijos
    while (children.length < p.population) {
      children.push(cloneCoords(population[order[0]]));
    }

    population = children;
    evaluations = population.map((c) => evaluator.evaluate(c));
    record(generation);
  }

  const finalIdx = getBestIndex();
  result.final = toPoints(population[finalIdx]);
  result.final_evaluation = evaluations[finalIdx];
  result.status = 'success';
  result.message = 'Búsqueda completada; no se garantiza óptimo global.';
  return result;
}
