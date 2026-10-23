"""Módulo de restricciones y validación de AstroShield (Integrante 3: Owen).

Proporciona la interfaz principal de factibilidad y re-exporta las herramientas
estructuradas del paquete backend.restrictions.
"""
from typing import Sequence, Any
import numpy as np
from .restrictions.validator import (
    validar_configuracion,
    validar_satelite,
    validar_zonas_restringidas,
    validar_objetos_existentes,
    validar_coordenadas,
    is_valid_point,
    detect_violations,
)
from .restrictions.models import (
    ViolationDetail,
    ValidationResult,
    ScenarioComparison,
)
from .restrictions.repair import (
    reparar_satelite,
    reparar_configuracion,
)

def violations(coords: Any, scenario: Any) -> list[str]:
    """Retorna lista de cadenas con las restricciones activas violadas ('S{i}: {nombre}').
    Mantiene compatibilidad total con backend.coverage y el resto de la aplicación.
    """
    return detect_violations(coords, scenario)

def valid_point(point: Any, scenario: Any) -> bool:
    """Determina si un punto es geográficamente factible y respeta todas las restricciones activas.
    Mantiene compatibilidad total con backend.evolution y backend.coverage.
    """
    return is_valid_point(point, scenario)

__all__ = [
    'violations',
    'valid_point',
    'validar_configuracion',
    'validar_satelite',
    'validar_zonas_restringidas',
    'validar_objetos_existentes',
    'validar_coordenadas',
    'is_valid_point',
    'detect_violations',
    'ViolationDetail',
    'ValidationResult',
    'ScenarioComparison',
    'reparar_satelite',
    'reparar_configuracion',
]
