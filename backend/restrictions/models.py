"""Modelos de datos para el módulo de restricciones y validación (Integrante 3: Owen)."""
from typing import Literal, Optional
from pydantic import BaseModel, Field

ViolationType = Literal[
    'zona_restringida',
    'objeto_existente',
    'coordenadas_invalidas',
    'cantidad_invalida'
]

class ViolationDetail(BaseModel):
    satelite: Optional[int] = Field(
        default=None,
        description="Índice del satélite infractor (1 a 8), o None si es global"
    )
    tipo: str = Field(
        description="Tipo de violación: zona_restringida, objeto_existente, coordenadas_invalidas, cantidad_invalida"
    )
    nombre: str = Field(
        description="Nombre de la zona restringida, objeto o descripción del error"
    )
    descripcion: str = Field(
        description="Explicación detallada de la violación cometida"
    )
    distancia_deg: Optional[float] = Field(
        default=None,
        description="Distancia angular calculada en grados respecto al centro de la restricción"
    )
    radio_limite_deg: Optional[float] = Field(
        default=None,
        description="Radio angular o radio de exclusión que fue invadido"
    )
    coordenadas: Optional[dict[str, float]] = Field(
        default=None,
        description="Coordenadas geográficas del satélite al momento de la infracción"
    )

class ValidationResult(BaseModel):
    valida: bool = Field(
        description="True si la constelación cumple el 100% de las restricciones; False en caso contrario"
    )
    total_satelites: int = Field(
        description="Cantidad total de satélites evaluados en la configuración"
    )
    total_violaciones: int = Field(
        description="Número de infracciones detectadas"
    )
    violaciones: list[ViolationDetail] = Field(
        default_factory=list,
        description="Listado exhaustivo y estructurado de las violaciones encontradas"
    )
    resumen: str = Field(
        default="",
        description="Resumen textual del dictamen de validación"
    )

class ScenarioComparison(BaseModel):
    anterior_valida: bool
    actual_valida: bool
    cambio_validez: bool
    resultado_anterior: ValidationResult
    resultado_actual: ValidationResult
    detalles: str
