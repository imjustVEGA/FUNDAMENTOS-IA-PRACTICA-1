export interface Point {
  lat: number;
  lon: number;
}

export interface Region extends Point {
  name: string;
  weight: number;
  radius_km?: number;
}

export interface Zone extends Point {
  name: string;
  radius_deg: number;
  active: boolean;
  kind?: 'debris' | 'object';
}

export interface Scenario {
  name: string;
  regions: Region[];
  zones: Zone[];
  footprint_km: number;
  samples: number;
}

export interface Parameters {
  seed: number;
  population: number;
  generations: number;
  crossover: number;
  mutation: number;
  tournament: number;
  elite: number;
  attempts: number;
}

export interface Coverage {
  name: string;
  fraction: number;
  covered: boolean;
  weight: number;
}

export interface Evaluation {
  valid: boolean;
  status: 'valid' | 'invalid' | 'valid_insufficient';
  fitness: number;
  covered_regions: number;
  coverage: Coverage[];
  violations: string[];
  separation_deg: number;
}

export interface Generation {
  generation: number;
  best: number;
  mean: number;
  worst: number;
  valid_count: number;
  best_configuration: Point[];
  covered_regions: number;
}

export interface Run {
  run_id?: string;
  status: 'success' | 'no_feasible_found';
  message: string;
  seed: number;
  parameters: Parameters;
  scenario: Scenario;
  initial?: Point[] | null;
  final?: Point[] | null;
  initial_evaluation?: Evaluation | null;
  final_evaluation?: Evaluation | null;
  history: Generation[];
}

export interface Comparison {
  before: Evaluation;
  after: Evaluation;
}

export interface ConfigurationPair {
  initial: Point[] | null;
  final: Point[] | null;
}
