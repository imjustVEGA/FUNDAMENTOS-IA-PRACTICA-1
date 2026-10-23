"""Operaciones geométricas sobre una esfera perfecta."""

from __future__ import annotations

import math

import numpy as np

# Modelo esférico; la altitud es solo ilustrativa y no interviene en cobertura.
R_TIERRA_KM = 6371.0
ALTITUD_SATELITE_KM = 550.0
RADIO_OBSERVACION_KM = 650.0
RADIO_REGION_KM = 300.0
UMBRAL_COBERTURA_REGION = 0.80


def normalizar_longitud(lon: float | np.ndarray) -> float | np.ndarray:
    """Normaliza longitud(es) al intervalo [-180, 180]."""
    normalizada = (np.asarray(lon, dtype=float) + 180.0) % 360.0 - 180.0
    if np.ndim(normalizada) == 0:
        return float(normalizada)
    return normalizada


def validar_coordenada(lat: float, lon: float) -> None:
    """Valida una latitud y longitud expresadas en grados."""
    try:
        latitud = float(lat)
        longitud = float(lon)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("La latitud y la longitud deben ser números finitos.") from exc
    if not math.isfinite(latitud) or not math.isfinite(longitud):
        raise ValueError("La latitud y la longitud deben ser números finitos.")
    if not -90.0 <= latitud <= 90.0:
        raise ValueError("La latitud debe estar entre -90 y 90 grados.")
    if not -180.0 <= longitud <= 180.0:
        raise ValueError("La longitud debe estar entre -180 y 180 grados.")


def _validar_arreglos_coordenadas(lat: np.ndarray, lon: np.ndarray) -> None:
    if (
        np.any(~np.isfinite(lat))
        or np.any(~np.isfinite(lon))
        or np.any((lat < -90.0) | (lat > 90.0))
        or np.any((lon < -180.0) | (lon > 180.0))
    ):
        raise ValueError("Coordenadas fuera de rango o no finitas.")


def km_a_angulo_central(
    radio_km: float | np.ndarray, r_esfera_km: float = R_TIERRA_KM
) -> float | np.ndarray:
    """Convierte una distancia superficial en ángulo central, en radianes."""
    radio = np.asarray(radio_km, dtype=float)
    if not math.isfinite(float(r_esfera_km)) or r_esfera_km <= 0:
        raise ValueError("El radio de la esfera debe ser positivo y finito.")
    if np.any(~np.isfinite(radio)) or np.any(radio < 0):
        raise ValueError("La distancia debe ser no negativa y finita.")
    angulo = radio / r_esfera_km
    if np.ndim(angulo) == 0:
        return float(angulo)
    return angulo


def distancia_haversine_km(
    lat1: float | np.ndarray,
    lon1: float | np.ndarray,
    lat2: float | np.ndarray,
    lon2: float | np.ndarray,
    r_esfera_km: float = R_TIERRA_KM,
) -> float | np.ndarray:
    """Calcula distancia de círculo máximo y permite broadcasting de arreglos."""
    if not math.isfinite(float(r_esfera_km)) or r_esfera_km <= 0:
        raise ValueError("El radio de la esfera debe ser positivo y finito.")
    latitud1, longitud1, latitud2, longitud2 = np.broadcast_arrays(
        np.asarray(lat1, dtype=float),
        np.asarray(lon1, dtype=float),
        np.asarray(lat2, dtype=float),
        np.asarray(lon2, dtype=float),
    )
    _validar_arreglos_coordenadas(latitud1, longitud1)
    _validar_arreglos_coordenadas(latitud2, longitud2)
    phi1 = np.deg2rad(latitud1)
    phi2 = np.deg2rad(latitud2)
    delta_phi = phi2 - phi1
    delta_lambda = np.deg2rad(
        np.asarray(normalizar_longitud(longitud2 - longitud1), dtype=float)
    )
    haversine = (
        np.sin(delta_phi / 2.0) ** 2
        + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0) ** 2
    )
    angulo = 2.0 * np.arcsin(np.sqrt(np.clip(haversine, 0.0, 1.0)))
    distancia = angulo * r_esfera_km
    if np.ndim(distancia) == 0:
        return float(distancia)
    return distancia


def punto_dentro_de_disco(
    lat: float,
    lon: float,
    lat_c: float,
    lon_c: float,
    radio_km: float,
) -> bool:
    """Indica si un punto está a no más del radio de un disco geodésico."""
    validar_coordenada(lat, lon)
    validar_coordenada(lat_c, lon_c)
    if not math.isfinite(float(radio_km)) or radio_km < 0:
        raise ValueError("El radio del disco debe ser no negativo y finito.")
    distancia = distancia_haversine_km(lat, lon, lat_c, lon_c)
    return distancia <= radio_km or math.isclose(
        distancia, radio_km, rel_tol=1e-12, abs_tol=1e-12
    )


def latlon_a_xyz(
    lat: float | np.ndarray,
    lon: float | np.ndarray,
    radio: float | np.ndarray,
) -> np.ndarray:
    """Convierte coordenadas geográficas a vectores XYZ cartesianos."""
    latitud, longitud, radio_arr = np.broadcast_arrays(
        np.asarray(lat, dtype=float),
        np.asarray(lon, dtype=float),
        np.asarray(radio, dtype=float),
    )
    _validar_arreglos_coordenadas(latitud, longitud)
    if np.any(~np.isfinite(radio_arr)) or np.any(radio_arr < 0):
        raise ValueError("El radio debe ser no negativo y finito.")
    phi = np.deg2rad(latitud)
    lam = np.deg2rad(longitud)
    x = radio_arr * np.cos(phi) * np.cos(lam)
    y = radio_arr * np.cos(phi) * np.sin(lam)
    z = radio_arr * np.sin(phi)
    return np.stack((x, y, z), axis=-1)


def destinos_geodesicos(lat: float, lon: float, angulos: np.ndarray, azimuts: np.ndarray) -> np.ndarray:
    """Destino sobre base tangente ortonormal, estable incluso exactamente en polos.

    Azimut cero apunta al norte local y pi/2 al este. Devuelve pares lat/lon.
    """
    validar_coordenada(lat, lon)
    a, b = np.radians([lat, lon])
    centro = latlon_a_xyz(lat, lon, 1)
    norte = np.array([-np.sin(a)*np.cos(b), -np.sin(a)*np.sin(b), np.cos(a)])
    este = np.array([-np.sin(b), np.cos(b), 0])
    t, az = np.broadcast_arrays(angulos, azimuts)
    direccion = np.cos(az)[..., None]*norte + np.sin(az)[..., None]*este
    puntos = np.cos(t)[..., None]*centro + np.sin(t)[..., None]*direccion
    latitudes = np.degrees(np.arctan2(puntos[..., 2], np.hypot(puntos[..., 0], puntos[..., 1])))
    longitudes = normalizar_longitud(np.degrees(np.arctan2(puntos[..., 1], puntos[..., 0])))
    return np.stack([latitudes, longitudes], axis=-1)
