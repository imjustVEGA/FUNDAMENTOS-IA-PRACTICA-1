"""Módulo validador de restricciones para satélites y constelaciones completas (Integrante 3: Owen).

Verifica:
- Exactamente 8 satélites por configuración.
- Coordenadas numéricas, finitas y dentro de [-90°, 90°] y [-180°, 180°].
- No invasión de las zonas restringidas de desechos espaciales activas.
- No invasión de los radios de exclusión de objetos existentes activos.
- Distinción estricta entre configuraciones inválidas y válidas con cobertura insuficiente.
"""
from typing import Any, Sequence
import numpy as np
from ..models import Point, Scenario, Zone
from .models import ViolationDetail, ValidationResult
from .geometry import distancia_angular, esta_en_o_sobre_limite, validar_rango_coordenadas

NUMERO_SATELITES_REQUERIDOS = 8

def extraer_coordenadas(satelite: Any) -> tuple[float, float]:
    """Extrae (lat, lon) desde Point, dict, tupla, lista o numpy array."""
    if isinstance(satelite, Point):
        return satelite.lat, satelite.lon
    if isinstance(satelite, dict):
        return satelite["lat"], satelite["lon"]
    if isinstance(satelite, (list, tuple, np.ndarray)) and len(satelite) >= 2:
        return satelite[0], satelite[1]
    raise ValueError(f"Formato de satélite no reconocido: {type(satelite).__name__}")

def validar_coordenadas(satelite: Any, satelite_idx: int = 1) -> list[ViolationDetail]:
    """Verifica que las coordenadas del satélite sean numéricas, finitas y estén en rango."""
    violaciones = []
    try:
        lat, lon = extraer_coordenadas(satelite)
    except Exception as e:
        violaciones.append(ViolationDetail(
            satelite=satelite_idx,
            tipo="coordenadas_invalidas",
            nombre="Formato inválido",
            descripcion=f"No se pudieron extraer coordenadas del satélite {satelite_idx}: {str(e)}"
        ))
        return violaciones

    valido, mensaje_error = validar_rango_coordenadas(lat, lon)
    if not valido:
        def finite_coordinate(value):
            try:
                number = float(value)
                return number if np.isfinite(number) else 0.0
            except (TypeError, ValueError, OverflowError):
                return 0.0
        violaciones.append(ViolationDetail(
            satelite=satelite_idx,
            tipo="coordenadas_invalidas",
            nombre="Límites geográficos",
            descripcion=f"El satélite {satelite_idx} tiene coordenadas fuera de rango: {mensaje_error}",
            coordenadas={"lat": finite_coordinate(lat), "lon": finite_coordinate(lon)}
        ))
    return violaciones

def validar_zonas_restringidas(satelite: Any, zonas: Sequence[Zone], satelite_idx: int = 1) -> list[ViolationDetail]:
    """Evalúa un satélite contra las zonas restringidas de desechos espaciales activas."""
    violaciones = []
    try:
        lat, lon = extraer_coordenadas(satelite)
        if not (np.isfinite(lat) and np.isfinite(lon)):
            return []
    except Exception:
        return []

    coord_sat = [lat, lon]
    for z in zonas:
        if not z.active:
            continue
        if getattr(z, 'kind', 'debris') == 'object':
            continue
        
        dist = distancia_angular(coord_sat, [z.lat, z.lon])
        if esta_en_o_sobre_limite(dist, z.radius_deg):
            violaciones.append(ViolationDetail(
                satelite=satelite_idx,
                tipo="zona_restringida",
                nombre=z.name,
                descripcion=f"El satélite {satelite_idx} invade la zona restringida '{z.name}' (distancia: {dist:.4f}°, radio límite: {z.radius_deg}°).",
                distancia_deg=round(float(dist), 4),
                radio_limite_deg=float(z.radius_deg),
                coordenadas={"lat": float(lat), "lon": float(lon)}
            ))
    return violaciones

def validar_objetos_existentes(satelite: Any, objetos: Sequence[Zone], satelite_idx: int = 1) -> list[ViolationDetail]:
    """Evalúa un satélite contra los radios de exclusión de los objetos existentes activos."""
    violaciones = []
    try:
        lat, lon = extraer_coordenadas(satelite)
        if not (np.isfinite(lat) and np.isfinite(lon)):
            return []
    except Exception:
        return []

    coord_sat = [lat, lon]
    for obj in objetos:
        if not obj.active:
            continue
        if getattr(obj, 'kind', 'debris') != 'object':
            continue
        
        dist = distancia_angular(coord_sat, [obj.lat, obj.lon])
        if esta_en_o_sobre_limite(dist, obj.radius_deg):
            violaciones.append(ViolationDetail(
                satelite=satelite_idx,
                tipo="objeto_existente",
                nombre=obj.name,
                descripcion=f"El satélite {satelite_idx} invade el radio de exclusión del objeto existente '{obj.name}' (distancia: {dist:.4f}°, radio de exclusión: {obj.radius_deg}°).",
                distancia_deg=round(float(dist), 4),
                radio_limite_deg=float(obj.radius_deg),
                coordenadas={"lat": float(lat), "lon": float(lon)}
            ))
    return violaciones

def validar_satelite(satelite: Any, escenario: Scenario, satelite_idx: int = 1) -> list[ViolationDetail]:
    """Valida individualmente un satélite contra todas las restricciones aplicables del escenario."""
    violaciones = []
    
    # 1. Comprobar coordenadas
    coord_errors = validar_coordenadas(satelite, satelite_idx)
    if coord_errors:
        violaciones.extend(coord_errors)
        return violaciones  # Si las coordenadas son corruptas/no finitas, no calculamos esférica
    
    # 2. Zonas restringidas (kind='debris')
    violaciones.extend(validar_zonas_restringidas(satelite, escenario.zones, satelite_idx))
    
    # 3. Objetos existentes (kind='object')
    violaciones.extend(validar_objetos_existentes(satelite, escenario.zones, satelite_idx))
    
    return violaciones

def validar_configuracion(satelites: Sequence[Any], escenario: Scenario) -> ValidationResult:
    """Valida exhaustivamente una configuración de constelación contra el escenario dado.
    
    Comprueba:
    1. Exactamente 8 satélites.
    2. Rango y validez de coordenadas.
    3. Ningún satélite invade zonas restringidas activas.
    4. Ningún satélite invade objetos existentes activos.
    
    Devuelve un ValidationResult estructurado con la lista detallada de violaciones.
    """
    violaciones: list[ViolationDetail] = []
    total_satelites = len(satelites) if satelites is not None else 0

    # Verificación de cantidad obligatoria de satélites
    if total_satelites != NUMERO_SATELITES_REQUERIDOS:
        violaciones.append(ViolationDetail(
            satelite=None,
            tipo="cantidad_invalida",
            nombre="Cantidad incorrecta de satélites",
            descripcion=f"Se requieren exactamente {NUMERO_SATELITES_REQUERIDOS} satélites en la constelación AstroShield, pero se recibieron {total_satelites}."
        ))

    # Validación individual de cada satélite presente
    if satelites is not None:
        for idx, sat in enumerate(satelites, start=1):
            violaciones.extend(validar_satelite(sat, escenario, satelite_idx=idx))

    es_valida = (len(violaciones) == 0)
    
    if es_valida:
        resumen = f"Configuración válida: los {total_satelites} satélites respetan todas las zonas restringidas y radios de exclusión."
    else:
        resumen = f"Configuración inválida: se detectaron {len(violaciones)} violaciones a las restricciones operativas."

    return ValidationResult(
        valida=es_valida,
        total_satelites=total_satelites,
        total_violaciones=len(violaciones),
        violaciones=violaciones,
        resumen=resumen
    )

# Funciones rápidas para el motor evolutivo y compatibilidad con coverage.py
def is_valid_point(point: Any, scenario: Scenario) -> bool:
    """Función de alto rendimiento para validar si un punto individual no viola restricciones activas.
    Reutilizada durante la inicialización y mutación del algoritmo genético.
    """
    try:
        lat, lon = extraer_coordenadas(point)
        lat, lon = float(lat), float(lon)
    except Exception:
        return False
    if not (np.isfinite(lat) and np.isfinite(lon)):
        return False
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        return False
    
    active_zones = [z for z in scenario.zones if z.active]
    if not active_zones:
        return True
    
    coords_zones = np.array([[z.lat, z.lon] for z in active_zones])
    radii = np.array([z.radius_deg for z in active_zones])
    
    distances = distancia_angular([lat, lon], coords_zones)
    return not bool(np.any(distances <= radii + 1e-9))

def detect_violations(coords: Any, scenario: Scenario) -> list[str]:
    """Genera lista de violaciones en formato string 'S{i+1}: {nombre}'
    compatible con backend.coverage y backend.constraints.
    """
    issues = []
    active_zones = [z for z in scenario.zones if z.active]
    if not active_zones:
        return issues
    
    coords_arr = np.asarray(coords, dtype=float)
    for z in active_zones:
        dists = distancia_angular(coords_arr, [z.lat, z.lon])
        violating_indices = np.flatnonzero(dists <= z.radius_deg + 1e-9)
        for i in violating_indices:
            issues.append(f'S{i+1}: {z.name}')
    return issues
