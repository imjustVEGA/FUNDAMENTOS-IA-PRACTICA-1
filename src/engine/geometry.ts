import type { PRNG } from './prng';

export const R_TIERRA_KM = 6371.0;

export function normalizarLongitud(lon: number): number {
  return ((lon + 180.0) % 360.0 + 360.0) % 360.0 - 180.0;
}

export type Vec3 = [number, number, number];

export function vectorFromCoord(lat: number, lon: number): Vec3 {
  const a = (lat * Math.PI) / 180.0;
  const b = (lon * Math.PI) / 180.0;
  return [
    Math.cos(a) * Math.cos(b),
    Math.cos(a) * Math.sin(b),
    Math.sin(a),
  ];
}

export function dot3(u: Vec3, v: Vec3): number {
  return u[0] * v[0] + u[1] * v[1] + u[2] * v[2];
}

export function cross3(u: Vec3, v: Vec3): Vec3 {
  return [
    u[1] * v[2] - u[2] * v[1],
    u[2] * v[0] - u[0] * v[2],
    u[0] * v[1] - u[1] * v[0],
  ];
}

export function norm3(u: Vec3): number {
  return Math.sqrt(u[0] * u[0] + u[1] * u[1] + u[2] * u[2]);
}

export function angularDistanceDeg(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const u = vectorFromCoord(lat1, lon1);
  const v = vectorFromCoord(lat2, lon2);
  const cross = cross3(u, v);
  const crossNorm = norm3(cross);
  const dot = dot3(u, v);
  return (Math.atan2(crossNorm, dot) * 180.0) / Math.PI;
}

export function haversineDistanceKm(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number,
  r = R_TIERRA_KM,
): number {
  const phi1 = (lat1 * Math.PI) / 180.0;
  const phi2 = (lat2 * Math.PI) / 180.0;
  const deltaPhi = phi2 - phi1;
  const deltaLambda = (normalizarLongitud(lon2 - lon1) * Math.PI) / 180.0;
  const h =
    Math.sin(deltaPhi / 2.0) ** 2 +
    Math.cos(phi1) * Math.cos(phi2) * Math.sin(deltaLambda / 2.0) ** 2;
  const clamped = Math.min(Math.max(h, 0.0), 1.0);
  return 2.0 * Math.asin(Math.sqrt(clamped)) * r;
}

export function destinosGeodesicos(
  lat: number,
  lon: number,
  t: number,
  az: number,
): [number, number] {
  const a = (lat * Math.PI) / 180.0;
  const b = (lon * Math.PI) / 180.0;
  const centro: Vec3 = [
    Math.cos(a) * Math.cos(b),
    Math.cos(a) * Math.sin(b),
    Math.sin(a),
  ];
  const norte: Vec3 = [
    -Math.sin(a) * Math.cos(b),
    -Math.sin(a) * Math.sin(b),
    Math.cos(a),
  ];
  const este: Vec3 = [-Math.sin(b), Math.cos(b), 0];

  const cosAz = Math.cos(az);
  const sinAz = Math.sin(az);
  const direccion: Vec3 = [
    cosAz * norte[0] + sinAz * este[0],
    cosAz * norte[1] + sinAz * este[1],
    cosAz * norte[2] + sinAz * este[2],
  ];

  const cosT = Math.cos(t);
  const sinT = Math.sin(t);
  const px = cosT * centro[0] + sinT * direccion[0];
  const py = cosT * centro[1] + sinT * direccion[1];
  const pz = cosT * centro[2] + sinT * direccion[2];

  const resLat = (Math.atan2(pz, Math.hypot(px, py)) * 180.0) / Math.PI;
  const resLon = normalizarLongitud((Math.atan2(py, px) * 180.0) / Math.PI);
  return [resLat, resLon];
}

/**
 * Muestreo cuasi-uniforme de un disco geodésico usando la espiral dorada de Fibonacci
 */
export function diskSamples(
  lat: number,
  lon: number,
  radiusKm: number,
  count: number,
): [number, number][] {
  const samples: [number, number][] = [];
  const cosRad = Math.cos(radiusKm / R_TIERRA_KM);
  const goldenFactor = Math.PI * (3.0 - Math.sqrt(5.0));

  for (let i = 0; i < count; i++) {
    const t = Math.acos(1.0 - ((i + 0.5) / count) * (1.0 - cosRad));
    const az = i * goldenFactor;
    samples.push(destinosGeodesicos(lat, lon, t, az));
  }
  return samples;
}

/**
 * Genera punto aleatorio uniforme sobre la esfera (lat, lon)
 */
export function uniformPoint(rng: PRNG): [number, number] {
  const z = rng.uniform(-1.0, 1.0);
  const lat = (Math.asin(z) * 180.0) / Math.PI;
  const lon = rng.uniform(-180.0, 180.0);
  return [lat, lon];
}

/**
 * Mutación sobre el plano tangente local: matemáticamente estable en cualquier latitud y polos
 */
export function move(
  point: [number, number],
  northDeg: number,
  eastDeg: number,
): [number, number] {
  const a = (point[0] * Math.PI) / 180.0;
  const b = (point[1] * Math.PI) / 180.0;
  const u: Vec3 = [
    Math.cos(a) * Math.cos(b),
    Math.cos(a) * Math.sin(b),
    Math.sin(a),
  ];
  const n: Vec3 = [
    -Math.sin(a) * Math.cos(b),
    -Math.sin(a) * Math.sin(b),
    Math.cos(a),
  ];
  const e: Vec3 = [-Math.sin(b), Math.cos(b), 0];

  const northRad = (northDeg * Math.PI) / 180.0;
  const eastRad = (eastDeg * Math.PI) / 180.0;

  const vx = u[0] + northRad * n[0] + eastRad * e[0];
  const vy = u[1] + northRad * n[1] + eastRad * e[1];
  const vz = u[2] + northRad * n[2] + eastRad * e[2];

  const norm = Math.sqrt(vx * vx + vy * vy + vz * vz);
  if (norm < 1e-9) return [point[0], point[1]];

  const nx = vx / norm;
  const ny = vy / norm;
  const nz = vz / norm;

  const latOut = (Math.asin(Math.max(-1.0, Math.min(1.0, nz))) * 180.0) / Math.PI;
  const lonOut = normalizarLongitud((Math.atan2(ny, nx) * 180.0) / Math.PI);
  return [latOut, lonOut];
}
