import type { OptimizationResponse, OptimizationState, RestrictedZone, OccupiedObject } from '../types/visualization';

const initialSatellites = [
  { id: 'SAT-1', lat: 52, lon: -142, isValid: true },
  { id: 'SAT-2', lat: -42, lon: -86, isValid: true },
  { id: 'SAT-3', lat: 8, lon: -30, isValid: true },
  { id: 'SAT-4', lat: 63, lon: 78, isValid: true },
  { id: 'SAT-5', lat: -54, lon: 151, isValid: true },
  { id: 'SAT-6', lat: 4, lon: 103, isValid: true },
  { id: 'SAT-7', lat: 28, lon: 31, isValid: true },
  { id: 'SAT-8', lat: -8, lon: -158, isValid: true },
];

const finalSatellites = [
  { id: 'SAT-1', lat: 21.0, lon: -89.0, isValid: true },
  { id: 'SAT-2', lat: -3.5, lon: -62.0, isValid: true },
  { id: 'SAT-3', lat: 36.8, lon: -119.4, isValid: true },
  { id: 'SAT-4', lat: 15.0, lon: 0.0, isValid: true },
  { id: 'SAT-5', lat: 36.0, lon: 138.0, isValid: true },
  { id: 'SAT-6', lat: -25.0, lon: 133.0, isValid: true },
  { id: 'SAT-7', lat: -12.0, lon: 20.0, isValid: true },
  { id: 'SAT-8', lat: 48.0, lon: 90.0, isValid: true },
];

const restrictedZones: RestrictedZone[] = [
  { name: 'Atlántico Norte', lat: 45, lon: -35, angularRadiusDeg: 12, type: 'restricted' },
  { name: 'Pacífico Sur', lat: -30, lon: -120, angularRadiusDeg: 10, type: 'restricted' },
  { name: 'Polar Norte', lat: 78, lon: 30, angularRadiusDeg: 8, type: 'restricted' },
];

const occupiedObjects: OccupiedObject[] = [
  { name: 'Objeto A', lat: 10, lon: 45, angularRadiusDeg: 5, type: 'occupied' },
  { name: 'Objeto B', lat: -15, lon: 110, angularRadiusDeg: 5, type: 'occupied' },
];

const makeState = (satellites: typeof initialSatellites, percentages: number[]): OptimizationState => {
  const regions = [
    { name: 'Península de Yucatán', lat: 20.5, lon: -89.0, priority: 'alta' as const, radiusKm: 300 },
    { name: 'Amazonía brasileña', lat: -3.5, lon: -62.0, priority: 'alta' as const, radiusKm: 300 },
    { name: 'California', lat: 36.8, lon: -119.4, priority: 'media' as const, radiusKm: 300 },
    { name: 'Sahel', lat: 15.0, lon: 0.0, priority: 'media' as const, radiusKm: 300 },
    { name: 'Japón', lat: 36.0, lon: 138.0, priority: 'media' as const, radiusKm: 300 },
    { name: 'Interior de Australia', lat: -25.0, lon: 133.0, priority: 'normal' as const, radiusKm: 300 },
  ];

  return {
    satellites,
    regions: regions.map((region, index) => ({
      ...region,
      coveragePercentage: percentages[index],
      isCovered: percentages[index] >= 80,
    })),
  };
};

/** Mock determinista para abrir el visor sin un backend conectado. */
export const mockOptimizationData: OptimizationResponse = {
  earthRadiusKm: 6371,
  initialState: makeState(initialSatellites, [28, 16, 34, 21, 39, 24]),
  finalState: makeState(finalSatellites, [98, 94, 88, 84, 91, 76]),
  restrictedZones,
  occupiedObjects,
};
