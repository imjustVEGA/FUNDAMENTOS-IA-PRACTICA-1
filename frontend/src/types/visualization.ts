/** Geografía en grados decimales; coincide con los campos lat/lon del API. */
export interface GeoCoordinate {
  lat: number;
  lon: number;
}

export interface Satellite extends GeoCoordinate {
  id: string;
  isValid: boolean;
}

export type RegionPriority = 'alta' | 'media' | 'normal';

export interface CoverageRegion extends GeoCoordinate {
  name: string;
  priority: RegionPriority;
  radiusKm: number;
  coveragePercentage: number;
  isCovered: boolean;
}

export interface RestrictedZone extends GeoCoordinate {
  name: string;
  angularRadiusDeg: number;
  type: 'restricted';
}

export interface OccupiedObject extends GeoCoordinate {
  name: string;
  angularRadiusDeg: number;
  type: 'occupied';
}

export type SpaceHazard = RestrictedZone | OccupiedObject;

/** Una solución del optimizador con posiciones y coberturas para el visor. */
export interface OptimizationState {
  satellites: Satellite[];
  regions: CoverageRegion[];
}

/** Respuesta normalizada que el adaptador del backend debe entregar al visor. */
export interface OptimizationResponse {
  earthRadiusKm: number;
  initialState: OptimizationState;
  finalState: OptimizationState;
  restrictedZones: RestrictedZone[];
  occupiedObjects: OccupiedObject[];
}

export type ConfigurationView = 'initial' | 'final' | 'comparison';

export type VisualizationSelection =
  | { kind: 'satellite'; data: Satellite; configuration: 'Inicial' | 'Final' }
  | { kind: 'region'; data: CoverageRegion; comparison?: { initial: number; final: number } }
  | { kind: 'restricted'; data: RestrictedZone }
  | { kind: 'occupied'; data: OccupiedObject };

export interface VisualizationLayers {
  satellites: boolean;
  footprints: boolean;
  regions: boolean;
  restrictedZones: boolean;
  occupiedObjects: boolean;
  autoRotate: boolean;
}
