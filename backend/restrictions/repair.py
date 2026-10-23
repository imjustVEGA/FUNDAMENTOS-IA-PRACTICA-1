"""Módulo de reparación acotada para individuos del algoritmo genético (Integrante 3: Owen).

Garantiza:
- Detección de satélites inválidos post-mutación o cruzamiento.
- Reparación acotada con presupuesto estricto de intentos para evitar bucles infinitos.
- Comunicación clara del motivo si no se logra la factibilidad dentro del presupuesto.
"""
from typing import Any, Sequence
import numpy as np
from ..geometry import uniform_point
from ..models import Scenario
from .validator import is_valid_point, extraer_coordenadas

def reparar_satelite(
    punto: Any,
    escenario: Scenario,
    rng: np.random.Generator | None = None,
    max_intentos: int = 300
) -> tuple[np.ndarray | None, int, str]:
    """Intenta reparar un satélite inválido mediante remuestreo uniforme acotado.
    
    Retorna:
    - punto_reparado: ndarray [lat, lon] o None si se agotó el presupuesto
    - intentos_usados: int
    - mensaje: str con el diagnóstico
    """
    if rng is None:
        rng = np.random.default_rng()

    try:
        coord = extraer_coordenadas(punto)
        if is_valid_point(coord, escenario):
            return np.array(coord, dtype=float), 0, "Satélite válido; no requirió reparación."
    except Exception:
        pass

    for intento in range(1, max_intentos + 1):
        candidato = uniform_point(rng)
        if is_valid_point(candidato, escenario):
            return candidato, intento, f"Satélite reparado con éxito en el intento {intento}."

    return None, max_intentos, (
        f"Presupuesto de {max_intentos} intentos agotado sin encontrar una posición válida. "
        "No demuestra matemáticamente imposibilidad, pero excede los recursos de búsqueda asignados."
    )

def reparar_configuracion(
    coordenadas: Sequence[Any],
    escenario: Scenario,
    rng: np.random.Generator | None = None,
    max_intentos: int = 300
) -> tuple[np.ndarray | None, dict[str, Any]]:
    """Repara de manera acotada una configuración completa de satélites (cromosoma).
    
    Retorna:
    - configuracion_reparada: ndarray de forma (N, 2) o None si algún satélite no pudo repararse
    - reporte: diccionario con estadísticas de intentos y estado por satélite
    """
    if rng is None:
        rng = np.random.default_rng()

    coords_arr = [np.array(extraer_coordenadas(p), dtype=float) for p in coordenadas]
    reparaciones = []
    total_intentos = 0

    for idx, sat in enumerate(coords_arr, start=1):
        reparado, intentos, msg = reparar_satelite(sat, escenario, rng=rng, max_intentos=max_intentos)
        total_intentos += intentos
        reparaciones.append({
            "satelite": idx,
            "exito": reparado is not None,
            "intentos": intentos,
            "mensaje": msg
        })
        if reparado is None:
            return None, {
                "exito": False,
                "total_intentos": total_intentos,
                "satelites_evaluados": idx,
                "detalle_reparacion": reparaciones,
                "motivo_fallo": f"El satélite {idx} no pudo ser reparado dentro de los {max_intentos} intentos."
            }
        coords_arr[idx - 1] = reparado

    return np.array(coords_arr), {
        "exito": True,
        "total_intentos": total_intentos,
        "satelites_evaluados": len(coords_arr),
        "detalle_reparacion": reparaciones,
        "motivo_fallo": None
    }
