import { BufferGeometry, Float32BufferAttribute, Vector3 } from 'three';
import type { GeoCoordinate } from '../types/visualization';

/** Radio terrestre medio empleado como base de escala del visor. */
export const EARTH_RADIUS_KM = 6371;
/** La Tierra ocupa cinco unidades en Three.js; toda altitud usa la misma escala. */
export const EARTH_RADIUS_SCENE = 5;
export const SATELLITE_ALTITUDE_KM = 550;
export const SATELLITE_RADIUS_SCENE = EARTH_RADIUS_SCENE * (EARTH_RADIUS_KM + SATELLITE_ALTITUDE_KM) / EARTH_RADIUS_KM;

/**
 * Proyecta latitud y longitud sobre una esfera centrada en el origen.
 * En esta convención el eje Y apunta al norte y el meridiano 0° mira a +Z.
 */
export function latLonToVector3(lat: number, lon: number, radius: number): Vector3 {
  const latitude = (lat * Math.PI) / 180;
  const longitude = (lon * Math.PI) / 180;
  const cosLatitude = Math.cos(latitude);

  return new Vector3(
    radius * cosLatitude * Math.sin(longitude),
    radius * Math.sin(latitude),
    radius * cosLatitude * Math.cos(longitude),
  );
}

export function coordinateToVector3(coordinate: GeoCoordinate, radius: number): Vector3 {
  return latLonToVector3(coordinate.lat, coordinate.lon, radius);
}

/** Convierte un radio geodésico medido en km al ángulo central correspondiente. */
export function kilometersToAngularRadius(radiusKm: number, earthRadiusKm = EARTH_RADIUS_KM): number {
  return radiusKm / earthRadiusKm;
}

/**
 * Crea un casquete geodésico curvo centrado en una coordenada.
 * Cada vértice se genera sobre la esfera mediante la fórmula de destino de círculo
 * máximo; por ello la huella nunca queda como un disco plano que corte la Tierra.
 * `angularRadius` se expresa en radianes y `surfaceOffset` separa capas cercanas.
 */
export function createSphericalCapGeometry(
  center: GeoCoordinate,
  angularRadius: number,
  sphereRadius = EARTH_RADIUS_SCENE,
  radialSegments = 8,
  angularSegments = 64,
  surfaceOffset = 0.012,
): BufferGeometry {
  const radius = sphereRadius + surfaceOffset;
  const centerNormal = coordinateToVector3(center, 1).normalize();
  const reference = Math.abs(centerNormal.y) > 0.94 ? new Vector3(1, 0, 0) : new Vector3(0, 1, 0);
  const tangentA = new Vector3().crossVectors(reference, centerNormal).normalize();
  const tangentB = new Vector3().crossVectors(centerNormal, tangentA).normalize();
  const positions: number[] = [];
  const indices: number[] = [];

  // Anillo 0 es el centro; los demás anillos llegan al borde angular del casquete.
  for (let ring = 0; ring <= radialSegments; ring += 1) {
    const distance = angularRadius * (ring / radialSegments);
    const sinDistance = Math.sin(distance);
    const cosDistance = Math.cos(distance);

    for (let segment = 0; segment <= angularSegments; segment += 1) {
      const bearing = (segment / angularSegments) * Math.PI * 2;
      const direction = tangentA.clone().multiplyScalar(Math.cos(bearing))
        .addScaledVector(tangentB, Math.sin(bearing));
      const point = centerNormal.clone().multiplyScalar(cosDistance)
        .addScaledVector(direction, sinDistance)
        .multiplyScalar(radius);
      positions.push(point.x, point.y, point.z);

      if (ring > 0 && segment > 0) {
        const current = ring * (angularSegments + 1) + segment;
        const previous = current - (angularSegments + 1);
        indices.push(previous - 1, previous, current - 1, previous, current, current - 1);
      }
    }
  }

  const geometry = new BufferGeometry();
  geometry.setAttribute('position', new Float32BufferAttribute(positions, 3));
  geometry.setIndex(indices);
  geometry.computeVertexNormals();
  return geometry;
}

/** Muestra una línea geodésica cerrada en el borde de un casquete. */
export function createSphericalBoundary(
  center: GeoCoordinate,
  angularRadius: number,
  sphereRadius = EARTH_RADIUS_SCENE,
  segments = 96,
  surfaceOffset = 0.018,
): Vector3[] {
  const centerNormal = coordinateToVector3(center, 1).normalize();
  const reference = Math.abs(centerNormal.y) > 0.94 ? new Vector3(1, 0, 0) : new Vector3(0, 1, 0);
  const tangentA = new Vector3().crossVectors(reference, centerNormal).normalize();
  const tangentB = new Vector3().crossVectors(centerNormal, tangentA).normalize();
  const ring: Vector3[] = [];

  for (let step = 0; step <= segments; step += 1) {
    const bearing = (step / segments) * Math.PI * 2;
    const direction = tangentA.clone().multiplyScalar(Math.cos(bearing))
      .addScaledVector(tangentB, Math.sin(bearing));
    ring.push(
      centerNormal.clone().multiplyScalar(Math.cos(angularRadius))
        .addScaledVector(direction, Math.sin(angularRadius))
        .multiplyScalar(sphereRadius + surfaceOffset),
    );
  }

  return ring;
}
