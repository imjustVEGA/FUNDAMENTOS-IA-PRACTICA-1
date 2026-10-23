"""Módulo de escenarios de AstroShield (Integrante 3: Owen).

Define el escenario base y re-exporta funciones de manipulación dinámica
de escenarios del paquete backend.restrictions.
"""
from .models import Scenario, Region, Zone
from .restrictions.scenarios import (
    base_scenario,
    activar_zona,
    desactivar_zona,
    modificar_radio_zona,
    agregar_zona_restringida,
    agregar_objeto_existente,
    actualizar_objeto,
    modificar_prioridad_region,
    guardar_escenario_json,
    cargar_escenario_json,
    reevaluar_configuracion_anterior,
    crear_escenario_a_normal,
    crear_escenario_b_espacio_reducido,
    crear_escenario_c_configuracion_invalida,
    crear_escenario_d_inviable,
    crear_escenario_e_cambio_condiciones,
    analizar_viabilidad_teorica,
    ZONAS_RESTINGIDAS_OBLIGATORIAS,
    OBJETOS_EXISTENTES_OBLIGATORIOS,
    REGIONES_TERRESTRES_BASE,
)

__all__ = [
    'Scenario',
    'Region',
    'Zone',
    'base_scenario',
    'activar_zona',
    'desactivar_zona',
    'modificar_radio_zona',
    'agregar_zona_restringida',
    'agregar_objeto_existente',
    'actualizar_objeto',
    'modificar_prioridad_region',
    'guardar_escenario_json',
    'cargar_escenario_json',
    'reevaluar_configuracion_anterior',
    'crear_escenario_a_normal',
    'crear_escenario_b_espacio_reducido',
    'crear_escenario_c_configuracion_invalida',
    'crear_escenario_d_inviable',
    'crear_escenario_e_cambio_condiciones',
    'analizar_viabilidad_teorica',
    'ZONAS_RESTINGIDAS_OBLIGATORIAS',
    'OBJETOS_EXISTENTES_OBLIGATORIOS',
    'REGIONES_TERRESTRES_BASE',
]
