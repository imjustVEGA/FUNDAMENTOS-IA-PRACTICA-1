"""Cobertura muestreada de regiones y fitness base por cobertura."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .regions import (
    N_MUESTRAS_REGION,
    SEMILLA_MUESTREO_PREDETERMINADA,
    RegionInteres,
    muestrear_region,
)
from .sphere_geometry import (
    RADIO_OBSERVACION_KM,
    UMBRAL_COBERTURA_REGION,
    distancia_haversine_km,
)


@dataclass(frozen=True)
class CoberturaRegion:
    """Fracción observada y flag de cobertura para una región."""

    region: RegionInteres
    fraccion: float
    cubierta: bool

    @property
    def nombre(self) -> str:
        """Nombre de la región cubierta."""
        return self.region.nombre

    @property
    def peso(self) -> float:
        """Peso usado al agregar resultados."""
        return float(self.region.peso)


def cobertura_por_region(
    satelites: np.ndarray | list[tuple[float, float]],
    regiones: tuple[RegionInteres, ...] | list[RegionInteres],
    radio_observacion_km: float = RADIO_OBSERVACION_KM,
) -> list[CoberturaRegion]:
    """Calcula unión de huellas sobre muestras, sin doble conteo."""
    coordenadas = np.asarray(satelites, dtype=float)
    if coordenadas.ndim != 2 or coordenadas.shape[1] != 2:
        raise ValueError("satelites debe tener forma (N, 2), con latitud y longitud.")
    if np.any(~np.isfinite(coordenadas)):
        raise ValueError("Las coordenadas de satélites deben ser finitas.")
    if np.any((coordenadas[:, 0] < -90) | (coordenadas[:, 0] > 90)):
        raise ValueError("La latitud de los satélites debe estar entre -90 y 90 grados.")
    if np.any((coordenadas[:, 1] < -180) | (coordenadas[:, 1] > 180)):
        raise ValueError("La longitud de los satélites debe estar entre -180 y 180 grados.")
    if not math.isfinite(float(radio_observacion_km)) or radio_observacion_km < 0:
        raise ValueError("El radio de observación debe ser no negativo y finito.")

    resultados: list[CoberturaRegion] = []
    for region in regiones:
        if region.muestras_lat is None or region.muestras_lon is None:
            muestras_lat, muestras_lon = muestrear_region(
                region, N_MUESTRAS_REGION, SEMILLA_MUESTREO_PREDETERMINADA
            )
        else:
            muestras_lat, muestras_lon = region.muestras_lat, region.muestras_lon

        if coordenadas.shape[0] == 0:
            fraccion = 0.0
        else:
            distancias = distancia_haversine_km(
                np.asarray(muestras_lat)[:, np.newaxis],
                np.asarray(muestras_lon)[:, np.newaxis],
                coordenadas[np.newaxis, :, 0],
                coordenadas[np.newaxis, :, 1],
            )
            cubiertas = np.any(distancias <= radio_observacion_km, axis=1)
            fraccion = float(np.count_nonzero(cubiertas) / cubiertas.size)
        resultados.append(
            CoberturaRegion(
                region=region,
                fraccion=fraccion,
                cubierta=fraccion >= UMBRAL_COBERTURA_REGION,
            )
        )
    return resultados


def _validar_coberturas(coberturas: list[CoberturaRegion]) -> float:
    if not coberturas:
        raise ValueError("Se requiere al menos una cobertura para calcular ponderaciones.")
    pesos = np.asarray([cobertura.peso for cobertura in coberturas], dtype=float)
    if np.any(~np.isfinite(pesos)) or np.any(pesos <= 0):
        raise ValueError("Los pesos de cobertura deben ser positivos y finitos.")
    return float(np.sum(pesos))


def cobertura_ponderada(coberturas: list[CoberturaRegion]) -> float:
    """Promedia las fracciones de cobertura según el peso de cada región."""
    peso_total = _validar_coberturas(coberturas)
    return float(
        sum(cobertura.peso * cobertura.fraccion for cobertura in coberturas) / peso_total
    )


def regiones_cubiertas_ponderadas(coberturas: list[CoberturaRegion]) -> float:
    """Calcula el peso relativo de las regiones que alcanzan el umbral."""
    peso_total = _validar_coberturas(coberturas)
    return float(
        sum(cobertura.peso for cobertura in coberturas if cobertura.cubierta) / peso_total
    )


def fitness_por_cobertura(coberturas: list[CoberturaRegion]) -> float:
    """Calcula fitness base en [0, 100], sin penalizaciones de restricciones."""
    cobertura = cobertura_ponderada(coberturas)
    regiones_cubiertas = regiones_cubiertas_ponderadas(coberturas)
    fitness = 100.0 * (0.80 * cobertura + 0.20 * regiones_cubiertas)
    return float(np.clip(fitness, 0.0, 100.0))
