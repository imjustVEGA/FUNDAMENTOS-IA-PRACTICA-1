"""Regiones de interés, discos restringidos y muestreo reproducible."""

from __future__ import annotations

from dataclasses import dataclass, replace
import math

import numpy as np

from .sphere_geometry import (
    RADIO_REGION_KM,
    R_TIERRA_KM,
    distancia_haversine_km,
    normalizar_longitud,
    validar_coordenada,
    destinos_geodesicos,
)

N_MUESTRAS_REGION = 1000
SEMILLA_MUESTREO_PREDETERMINADA = 0
_PESOS_PRIORIDAD = {"alta": 3.0, "media": 2.0, "normal": 1.0}


@dataclass(frozen=True)
class RegionInteres:
    """Región de interés y, opcionalmente, sus muestras precomputadas."""

    nombre: str
    lat: float
    lon: float
    prioridad: str
    peso: float | None = None
    muestras_lat: np.ndarray | None = None
    muestras_lon: np.ndarray | None = None

    def __post_init__(self) -> None:
        validar_coordenada(self.lat, self.lon)
        if self.prioridad not in _PESOS_PRIORIDAD:
            raise ValueError(f"Prioridad desconocida: {self.prioridad}")
        peso = _PESOS_PRIORIDAD[self.prioridad] if self.peso is None else self.peso
        if not math.isfinite(float(peso)) or peso <= 0:
            raise ValueError("El peso debe ser positivo y finito.")
        object.__setattr__(self, "peso", float(peso))
        if (self.muestras_lat is None) != (self.muestras_lon is None):
            raise ValueError("Las dos coordenadas de las muestras deben estar presentes.")
        if self.muestras_lat is not None:
            latitudes, longitudes = np.broadcast_arrays(
                np.asarray(self.muestras_lat, dtype=float),
                np.asarray(self.muestras_lon, dtype=float),
            )
            if latitudes.ndim != 1 or latitudes.size == 0:
                raise ValueError("Las muestras deben ser arreglos unidimensionales no vacíos.")
            if (
                np.any(~np.isfinite(latitudes))
                or np.any(~np.isfinite(longitudes))
                or np.any((latitudes < -90) | (latitudes > 90))
                or np.any((longitudes < -180) | (longitudes > 180))
            ):
                raise ValueError("Las muestras contienen coordenadas inválidas.")
            object.__setattr__(self, "muestras_lat", latitudes)
            object.__setattr__(self, "muestras_lon", longitudes)


@dataclass(frozen=True)
class ZonaRestringida:
    """Disco geodésico restringido con radio angular expresado en grados."""

    nombre: str
    lat: float
    lon: float
    radio_grados: float

    def __post_init__(self) -> None:
        validar_coordenada(self.lat, self.lon)
        if not math.isfinite(float(self.radio_grados)) or self.radio_grados < 0:
            raise ValueError("El radio angular debe ser no negativo y finito.")


@dataclass(frozen=True)
class ObjetoOcupado:
    """Disco geodésico ocupado con radio angular expresado en grados."""

    nombre: str
    lat: float
    lon: float
    radio_grados: float

    def __post_init__(self) -> None:
        validar_coordenada(self.lat, self.lon)
        if not math.isfinite(float(self.radio_grados)) or self.radio_grados < 0:
            raise ValueError("El radio angular debe ser no negativo y finito.")


_REGIONES_SIN_MUESTRAS = (
    RegionInteres("Península de Yucatán", 20.5, -89.0, "alta"),
    RegionInteres("Amazonía brasileña", -3.5, -62.0, "alta"),
    RegionInteres("California", 36.8, -119.4, "media"),
    RegionInteres("Sahel", 15.0, 0.0, "media"),
    RegionInteres("Japón", 36.0, 138.0, "media"),
    RegionInteres("Interior de Australia", -25.0, 133.0, "normal"),
)

ZONAS_RESTRINGIDAS_BASE = (
    ZonaRestringida("Atlántico Norte", 45.0, -35.0, 12.0),
    ZonaRestringida("Pacífico Sur", -30.0, -120.0, 10.0),
    ZonaRestringida("Polar norte", 78.0, 30.0, 8.0),
)

OBJETOS_OCUPADOS_BASE = (
    ObjetoOcupado("Objeto A", 10.0, 45.0, 5.0),
    ObjetoOcupado("Objeto B", -15.0, 110.0, 5.0),
)


def _hash_nombre_estable(nombre: str) -> int:
    """Genera un entero estable entre procesos para sembrar el generador."""
    resultado = 0
    for caracter in nombre:
        resultado = (resultado * 31 + ord(caracter)) & 0xFFFFFFFF
    return resultado


def muestrear_region(
    region: RegionInteres, n: int, semilla: int
) -> tuple[np.ndarray, np.ndarray]:
    """Muestrea uniformemente en área un disco geodésico de 300 km."""
    if not isinstance(n, (int, np.integer)) or n <= 0:
        raise ValueError("n debe ser un entero positivo.")
    if not isinstance(semilla, (int, np.integer)):
        raise ValueError("La semilla debe ser un entero.")
    rng = np.random.default_rng((int(semilla) + _hash_nombre_estable(region.nombre)) % 2**64)
    delta_max = RADIO_REGION_KM / R_TIERRA_KM
    u = rng.uniform(0.0, 1.0, size=n)
    theta = rng.uniform(0.0, 2.0 * np.pi, size=n)
    distancia = np.arccos(1.0 - u * (1.0 - np.cos(delta_max)))
    puntos = destinos_geodesicos(region.lat, region.lon, distancia, theta)
    return puntos[:, 0], puntos[:, 1]


def precomputar_muestras(
    regiones: tuple[RegionInteres, ...] | list[RegionInteres] = _REGIONES_SIN_MUESTRAS,
    n: int = N_MUESTRAS_REGION,
    semilla: int = SEMILLA_MUESTREO_PREDETERMINADA,
) -> tuple[RegionInteres, ...]:
    """Devuelve las regiones con muestras fijas y reproducibles."""
    resultado = []
    for region in regiones:
        muestras_lat, muestras_lon = muestrear_region(region, n, semilla)
        resultado.append(
            replace(region, muestras_lat=muestras_lat, muestras_lon=muestras_lon)
        )
    return tuple(resultado)


REGIONES_BASE = precomputar_muestras(_REGIONES_SIN_MUESTRAS)


def satelite_en_zona(lat: float, lon: float, zona: ZonaRestringida | ObjetoOcupado) -> bool:
    """Indica si un satélite está dentro de un disco angular restringido."""
    validar_coordenada(lat, lon)
    distancia_angular = distancia_haversine_km(lat, lon, zona.lat, zona.lon) / R_TIERRA_KM
    return distancia_angular <= math.radians(zona.radio_grados)


def satelite_en_alguna_zona(
    lat: float,
    lon: float,
    zonas: tuple[ZonaRestringida, ...] | list[ZonaRestringida],
    objetos: tuple[ObjetoOcupado, ...] | list[ObjetoOcupado],
) -> bool:
    """Indica si un satélite pertenece a alguna zona u objeto ocupado."""
    return any(satelite_en_zona(lat, lon, disco) for disco in (*zonas, *objetos))
