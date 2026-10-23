"""Utilidades geométricas y de distancia esférica para validación de restricciones.
Reutiliza las funciones de esfera del Integrante 2 (backend.geometry).
"""
import numpy as np
from ..geometry import angular, vectors, R

def distancia_angular(a, b) -> float:
    """Calcula la distancia angular esférica (en grados) entre dos puntos [lat, lon].
    
    Utiliza el producto punto y producto cruz de vectores unitarios tridimensionales,
    lo cual es numéricamente estable cerca de los polos geográficos (lat +/- 90°)
    y al cruzar el antimeridiano (lon +/- 180°).
    """
    res = angular(a, b)
    if isinstance(res, np.ndarray) and res.ndim == 0:
        return float(res)
    return res

def esta_en_o_sobre_limite(distancia_deg: float, radio_limite_deg: float, tolerancia: float = 1e-9) -> bool:
    """Determina si una distancia angular invade o se encuentra exactamente sobre el límite
    del radio angular de exclusión.
    
    Tanto los puntos estrictamente interiores como los situados sobre la frontera
    se consideran violaciones de la restricción.
    """
    return bool(distancia_deg <= (radio_limite_deg + tolerancia))

def validar_rango_coordenadas(lat: float, lon: float) -> tuple[bool, str]:
    """Comprueba que las coordenadas sean numéricas, finitas y estén en los rangos válidos:
    Latitud: [-90°, 90°]
    Longitud: [-180°, 180°]
    """
    try:
        flat = float(lat)
        flon = float(lon)
    except (TypeError, ValueError):
        return False, f"Coordenadas no numéricas: lat={lat}, lon={lon}"
    
    if not (np.isfinite(flat) and np.isfinite(flon)):
        return False, f"Coordenadas no finitas (NaN o Infinito detectado): lat={flat}, lon={flon}"
    
    if not (-90.0 <= flat <= 90.0):
        return False, f"Latitud fuera del rango permitido [-90°, 90°]: {flat}°"
    
    if not (-180.0 <= flon <= 180.0):
        return False, f"Longitud fuera del rango permitido [-180°, 180°]: {flon}°"
    
    return True, ""
