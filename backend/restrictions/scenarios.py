"""Módulo de escenarios dinámicos y escenarios difíciles (Integrante 3: Owen).

Permite:
- Activar o desactivar zonas y objetos.
- Agregar nuevas zonas restringidas y objetos existentes.
- Modificar radios de exclusión y posiciones.
- Modificar prioridades de regiones.
- Serialización y recuperación en JSON.
- Revalidación de soluciones anteriores ante cambios de restricciones.
- Provisión de Escenarios de prueba A, B, C, D e Inviables.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Sequence, Any
from ..models import Scenario, Region, Zone, Point
from .models import ValidationResult, ScenarioComparison
from .validator import validar_configuracion

# 1. Definiciones obligatorias de zonas restringidas y objetos existentes
ZONAS_RESTINGIDAS_OBLIGATORIAS: list[Zone] = [
    Zone(name='Atlántico Norte', lat=45.0, lon=-35.0, radius_deg=12.0, active=True, kind='debris'),
    Zone(name='Pacífico Sur', lat=-30.0, lon=-120.0, radius_deg=10.0, active=True, kind='debris'),
    Zone(name='Polar norte', lat=78.0, lon=30.0, radius_deg=8.0, active=True, kind='debris'),
]

OBJETOS_EXISTENTES_OBLIGATORIOS: list[Zone] = [
    Zone(name='Objeto A', lat=10.0, lon=45.0, radius_deg=5.0, active=True, kind='object'),
    Zone(name='Objeto B', lat=-15.0, lon=110.0, radius_deg=5.0, active=True, kind='object'),
]

REGIONES_TERRESTRES_BASE: list[Region] = [
    Region(name='Península de Yucatán', lat=20.5, lon=-89.0, weight=3.0),
    Region(name='Amazonía brasileña', lat=-3.5, lon=-62.0, weight=3.0),
    Region(name='California', lat=36.8, lon=-119.4, weight=2.0),
    Region(name='Sahel', lat=15.0, lon=0.0, weight=2.0),
    Region(name='Japón', lat=36.0, lon=138.0, weight=2.0),
    Region(name='Interior de Australia', lat=-25.0, lon=133.0, weight=1.0),
]

def base_scenario() -> Scenario:
    """Genera el escenario base oficial de AstroShield con 3 zonas y 2 objetos."""
    return Scenario(
        name='Base',
        regions=[r.model_copy() for r in REGIONES_TERRESTRES_BASE],
        zones=[z.model_copy() for z in (ZONAS_RESTINGIDAS_OBLIGATORIAS + OBJETOS_EXISTENTES_OBLIGATORIOS)],
        footprint_km=650.0,
        samples=128
    )

# 2. Métodos dinámicos para modificar condiciones del escenario
def activar_zona(escenario: Scenario, nombre: str, activo: bool = True) -> bool:
    """Activa o desactiva una zona u objeto por nombre."""
    for z in escenario.zones:
        if z.name.strip().lower() == nombre.strip().lower():
            z.active = activo
            return True
    return False

def desactivar_zona(escenario: Scenario, nombre: str) -> bool:
    """Desactiva una zona u objeto por nombre."""
    return activar_zona(escenario, nombre, activo=False)

def modificar_radio_zona(escenario: Scenario, nombre: str, nuevo_radio_deg: float) -> bool:
    """Modifica el radio angular (o radio de exclusión) de una zona u objeto."""
    if not (0 < nuevo_radio_deg <= 180):
        raise ValueError("El radio angular debe ser mayor a 0° y menor o igual a 180°.")
    for z in escenario.zones:
        if z.name.strip().lower() == nombre.strip().lower():
            z.radius_deg = float(nuevo_radio_deg)
            return True
    return False

def agregar_zona_restringida(
    escenario: Scenario,
    nombre: str,
    lat: float,
    lon: float,
    radio_deg: float,
    activo: bool = True
) -> Zone:
    """Agrega una nueva zona restringida por desechos espaciales (kind='debris')."""
    if len(escenario.zones) >= 50:
        raise ValueError("No se pueden agregar más de 50 zonas en un escenario.")
    nueva_zona = Zone(name=nombre, lat=lat, lon=lon, radius_deg=radio_deg, active=activo, kind='debris')
    escenario.zones.append(nueva_zona)
    return nueva_zona

def agregar_objeto_existente(
    escenario: Scenario,
    nombre: str,
    lat: float,
    lon: float,
    radio_exclusion_deg: float,
    activo: bool = True
) -> Zone:
    """Agrega un nuevo objeto existente ocupando posición (kind='object')."""
    if len(escenario.zones) >= 50:
        raise ValueError("No se pueden agregar más de 50 zonas u objetos en un escenario.")
    nuevo_objeto = Zone(
        name=nombre,
        lat=lat,
        lon=lon,
        radius_deg=radio_exclusion_deg,
        active=activo,
        kind='object'
    )
    escenario.zones.append(nuevo_objeto)
    return nuevo_objeto

def actualizar_objeto(
    escenario: Scenario,
    nombre: str,
    lat: float | None = None,
    lon: float | None = None,
    radio_exclusion_deg: float | None = None,
    activo: bool | None = None
) -> bool:
    """Actualiza la posición, radio o estado de un objeto existente."""
    for z in escenario.zones:
        if z.name.strip().lower() == nombre.strip().lower() and getattr(z, 'kind', 'debris') == 'object':
            if lat is not None:
                z.lat = float(lat)
            if lon is not None:
                z.lon = float(lon)
            if radio_exclusion_deg is not None:
                if not (0 < radio_exclusion_deg <= 180):
                    raise ValueError("El radio de exclusión debe estar entre 0° y 180°.")
                z.radius_deg = float(radio_exclusion_deg)
            if activo is not None:
                z.active = bool(activo)
            return True
    return False

def modificar_prioridad_region(escenario: Scenario, nombre_region: str, nuevo_peso: float) -> bool:
    """Modifica el peso/prioridad de una de las seis regiones terrestres."""
    if not (0 < nuevo_peso <= 100):
        raise ValueError("El peso debe estar entre 0 y 100.")
    for r in escenario.regions:
        if r.name.strip().lower() == nombre_region.strip().lower():
            r.weight = float(nuevo_peso)
            return True
    return False

# 3. Guardado y recuperación en formato JSON
def guardar_escenario_json(escenario: Scenario, destino: str | Path) -> str:
    """Guarda la definición completa del escenario en un archivo JSON."""
    p = Path(destino)
    p.parent.mkdir(parents=True, exist_ok=True)
    contenido = escenario.model_dump_json(indent=2)
    p.write_text(contenido, encoding='utf-8')
    return str(p)

def cargar_escenario_json(origen: str | Path | dict) -> Scenario:
    """Recupera un escenario desde un archivo JSON, un string JSON o un diccionario."""
    if isinstance(origen, dict):
        return Scenario.model_validate(origen)
    if isinstance(origen, Path) or (isinstance(origen, str) and not origen.strip().startswith('{')):
        p = Path(origen)
        contenido = p.read_text(encoding='utf-8')
        return Scenario.model_validate_json(contenido)
    return Scenario.model_validate_json(origen)

# 4. Reevaluación de configuraciones anteriores tras cambiar condiciones
def reevaluar_configuracion_anterior(
    configuracion: Sequence[Any],
    escenario_anterior: Scenario,
    escenario_nuevo: Scenario
) -> ScenarioComparison:
    """Evalúa una configuración existente ante un cambio en las condiciones del escenario.
    
    Comprueba si la solución previa continúa siendo válida y explica qué restricciones
    se incumplen si dejó de ser factible.
    """
    res_anterior = validar_configuracion(configuracion, escenario_anterior)
    res_actual = validar_configuracion(configuracion, escenario_nuevo)
    
    cambio = (res_anterior.valida != res_actual.valida)
    
    if res_anterior.valida and not res_actual.valida:
        nombres_infracciones = [v.nombre for v in res_actual.violaciones]
        detalles = (
            f"La configuración previa ERA válida en '{escenario_anterior.name}', "
            f"pero es INVÁLIDA en '{escenario_nuevo.name}'. "
            f"Violaciones nuevas detectadas: {', '.join(set(nombres_infracciones))}."
        )
    elif not res_anterior.valida and res_actual.valida:
        detalles = (
            f"La configuración previa ERA inválida en '{escenario_anterior.name}', "
            f"y ahora es VÁLIDA en '{escenario_nuevo.name}' debido a la flexibilización de restricciones."
        )
    elif res_anterior.valida and res_actual.valida:
        detalles = f"La configuración continúa siendo válida bajo las nuevas condiciones de '{escenario_nuevo.name}'."
    else:
        detalles = f"La configuración sigue siendo inválida en ambos escenarios ({len(res_actual.violaciones)} violaciones actuales)."

    return ScenarioComparison(
        anterior_valida=res_anterior.valida,
        actual_valida=res_actual.valida,
        cambio_validez=cambio,
        resultado_anterior=res_anterior,
        resultado_actual=res_actual,
        detalles=detalles
    )

# 5. Escenarios difíciles y condiciones inviables (Escenarios A - E)
def crear_escenario_a_normal() -> Scenario:
    """Escenario A — Normal:
    Utiliza exactamente las tres zonas restringidas y los dos objetos originales.
    """
    s = base_scenario()
    s.name = 'Escenario A - Normal'
    return s

def crear_escenario_b_espacio_reducido() -> Scenario:
    """Escenario B — Espacio reducido:
    Agrega nuevas restricciones de desechos espaciales y expande radios de exclusión
    para reducir drásticamente el espacio factible en la superficie esférica.
    """
    s = base_scenario()
    s.name = 'Escenario B - Espacio reducido'
    # Incrementar radio de Atlántico Norte de 12° a 25°
    modificar_radio_zona(s, 'Atlántico Norte', 25.0)
    # Incrementar radio de Pacífico Sur de 10° a 20°
    modificar_radio_zona(s, 'Pacífico Sur', 20.0)
    # Agregar 3 zonas de exclusión adicionales sobre corredores orbitales clave
    agregar_zona_restringida(s, 'Cinturón Ecuatorial Debris', lat=0.0, lon=0.0, radio_deg=18.0)
    agregar_zona_restringida(s, 'Sector Índico Denso', lat=-10.0, lon=75.0, radio_deg=15.0)
    agregar_zona_restringida(s, 'Sector Atlántico Sur', lat=-40.0, lon=-20.0, radio_deg=16.0)
    return s

def crear_escenario_c_configuracion_invalida() -> tuple[Scenario, list[Point]]:
    """Escenario C — Configuración inválida:
    Retorna el escenario base y una constelación de 8 satélites donde intencionalmente
    se ubican satélites invadiendo zonas restringidas y radios de objetos.
    
    - Satélite 1: Dentro de Atlántico Norte (lat 45°, lon -35°)
    - Satélite 2: Dentro del Objeto A (lat 10°, lon 45°)
    - Satélite 3: En el límite exacto del Pacífico Sur (lat -30°, lon -110°) -> a 10°
    - Satélites 4 a 8: Posiciones sin violaciones
    """
    s = base_scenario()
    s.name = 'Escenario C - Detección de Violaciones'
    
    configuracion_invalida = [
        Point(lat=45.0, lon=-35.0),      # S1: Centro de Atlántico Norte (debe fallar por zona_restringida)
        Point(lat=10.0, lon=45.0),       # S2: Centro de Objeto A (debe fallar por objeto_existente)
        Point(lat=-30.0, lon=-110.0),    # S3: A 10.0° del Pacífico Sur (-30, -120), sobre el borde (debe fallar)
        Point(lat=0.0, lon=10.0),        # S4: Válido
        Point(lat=-20.0, lon=-50.0),     # S5: Válido
        Point(lat=60.0, lon=120.0),      # S6: Válido
        Point(lat=-60.0, lon=60.0),      # S7: Válido
        Point(lat=25.0, lon=-140.0),     # S8: Válido
    ]
    return s, configuracion_invalida

def crear_escenario_d_inviable() -> Scenario:
    """Escenario D — Condición inviable demostrada:
    Construye un escenario que excluye toda la superficie disponible mediante una
    restricción con radio angular de 180°.
    
    Cualquier punto sobre la esfera terrestre dista <= 180° del centro, haciendo
    que matemáticamente el conjunto factible sea vacío (vacuously empty).
    """
    s = base_scenario()
    s.name = 'Escenario D - Condición Inviable (180°)'
    agregar_zona_restringida(s, 'Exclusión Total Global', lat=0.0, lon=0.0, radio_deg=180.0)
    return s

def crear_escenario_e_cambio_condiciones() -> tuple[Scenario, Scenario, list[Point]]:
    """Escenario E — Cambio de condiciones:
    Construye un escenario inicial con una solución válida. Luego añade una nueva
    restricción que intersecta uno de los satélites, para demostrar la capacidad
    de reevaluar y explicar el motivo por el cual la configuración dejó de ser válida.
    """
    s_inicial = base_scenario()
    s_inicial.name = 'Escenario E - Inicial'
    
    # 8 posiciones válidas en el escenario inicial
    solucion = [
        Point(lat=20.5, lon=-89.0),      # S1: Yucatán
        Point(lat=-3.5, lon=-62.0),      # S2: Amazonía
        Point(lat=36.8, lon=-119.4),     # S3: California
        Point(lat=15.0, lon=0.0),        # S4: Sahel
        Point(lat=36.0, lon=138.0),      # S5: Japón
        Point(lat=-25.0, lon=133.0),     # S6: Australia
        Point(lat=0.0, lon=30.0),        # S7: Punto neutral
        Point(lat=-45.0, lon=0.0),       # S8: Punto neutral
    ]
    
    # Escenario modificado: se coloca una nueva zona de desechos bloqueando a S1 (Yucatán)
    s_modificado = s_inicial.model_copy(deep=True)
    s_modificado.name = 'Escenario E - Modificado (Restricción Sobrevenida)'
    agregar_zona_restringida(
        s_modificado,
        nombre='Nube de Desechos Yucatán',
        lat=20.5,
        lon=-89.0,
        radio_deg=5.0
    )
    
    return s_inicial, s_modificado, solucion

def analizar_viabilidad_teorica(escenario: Scenario) -> dict[str, Any]:
    """Analiza matemáticamente si el escenario es demostrablemente inviable
    o si requiere exploración estocástica acotada.
    """
    for z in escenario.zones:
        if z.active and z.radius_deg >= 180.0:
            return {
                "inviable_demostrado": True,
                "motivo": f"La restricción activa '{z.name}' tiene un radio de {z.radius_deg}° que cubre el 100% de la esfera.",
                "area_disponible_porcentaje": 0.0
            }
    return {
        "inviable_demostrado": False,
        "motivo": "No existen restricciones globales de 180°. La factibilidad depende de la distribución espacial.",
        "area_disponible_porcentaje": None
    }
