import type { Scenario, Region, Zone } from '../types';

export const REGIONES_TERRESTRES_BASE: Region[] = [
  { lat: 20.5, lon: -89.0, name: 'Península de Yucatán', weight: 3.0, radius_km: 300.0 },
  { lat: -3.5, lon: -62.0, name: 'Amazonía brasileña', weight: 3.0, radius_km: 300.0 },
  { lat: 36.8, lon: -119.4, name: 'California', weight: 2.0, radius_km: 300.0 },
  { lat: 15.0, lon: 0.0, name: 'Sahel', weight: 2.0, radius_km: 300.0 },
  { lat: 36.0, lon: 138.0, name: 'Japón', weight: 2.0, radius_km: 300.0 },
  { lat: -25.0, lon: 133.0, name: 'Interior de Australia', weight: 1.0, radius_km: 300.0 },
];

export const ZONAS_RESTINGIDAS_OBLIGATORIAS: Zone[] = [
  { lat: 45.0, lon: -35.0, name: 'Atlántico Norte', radius_deg: 12.0, active: true, kind: 'debris' },
  { lat: -30.0, lon: -120.0, name: 'Pacífico Sur', radius_deg: 10.0, active: true, kind: 'debris' },
  { lat: 78.0, lon: 30.0, name: 'Polar norte', radius_deg: 8.0, active: true, kind: 'debris' },
];

export const OBJETOS_EXISTENTES_OBLIGATORIOS: Zone[] = [
  { lat: 10.0, lon: 45.0, name: 'Objeto A', radius_deg: 5.0, active: true, kind: 'object' },
  { lat: -15.0, lon: 110.0, name: 'Objeto B', radius_deg: 5.0, active: true, kind: 'object' },
];

export function baseScenario(): Scenario {
  return {
    name: 'Base',
    regions: REGIONES_TERRESTRES_BASE.map((r) => ({ ...r })),
    zones: [
      ...ZONAS_RESTINGIDAS_OBLIGATORIAS.map((z) => ({ ...z })),
      ...OBJETOS_EXISTENTES_OBLIGATORIOS.map((z) => ({ ...z })),
    ],
    footprint_km: 650.0,
    samples: 128,
  };
}

export function crearEscenarioBEspacioReducido(): Scenario {
  const s = baseScenario();
  s.name = 'Escenario B - Espacio reducido';
  for (const z of s.zones) {
    if (z.name === 'Atlántico Norte') z.radius_deg = 25.0;
    if (z.name === 'Pacífico Sur') z.radius_deg = 20.0;
  }
  s.zones.push(
    { lat: 0.0, lon: 0.0, name: 'Cinturón Ecuatorial Debris', radius_deg: 18.0, active: true, kind: 'debris' },
    { lat: -10.0, lon: 75.0, name: 'Sector Índico Denso', radius_deg: 15.0, active: true, kind: 'debris' },
    { lat: -40.0, lon: -20.0, name: 'Sector Atlántico Sur', radius_deg: 16.0, active: true, kind: 'debris' },
  );
  return s;
}

export function crearEscenarioDInviable(): Scenario {
  const s = baseScenario();
  s.name = 'Escenario D - Condición Inviable (180°)';
  s.zones.push({
    lat: 0.0,
    lon: 0.0,
    name: 'Exclusión Total Global',
    radius_deg: 180.0,
    active: true,
    kind: 'debris',
  });
  return s;
}

export function crearEscenarioECambioCondiciones(): {
  initial: Scenario;
  changed: Scenario;
} {
  const initial = baseScenario();
  initial.name = 'Escenario E - Inicial';

  const changed = baseScenario();
  changed.name = 'Escenario E - Modificado (Restricción Sobrevenida)';
  changed.zones.push({
    lat: 20.5,
    lon: -89.0,
    name: 'Nube de Desechos Yucatán',
    radius_deg: 5.0,
    active: true,
    kind: 'debris',
  });

  return { initial, changed };
}

export function getPresetScenarios(): Record<string, Scenario> {
  const { changed } = crearEscenarioECambioCondiciones();
  return {
    base: baseScenario(),
    reduced: crearEscenarioBEspacioReducido(),
    changed,
    impossible: crearEscenarioDInviable(),
  };
}
