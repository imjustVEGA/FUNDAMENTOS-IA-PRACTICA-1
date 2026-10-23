"""Pruebas unitarias de los dos objetos existentes con posiciones ocupadas (Integrante 3: Owen)."""
import pytest
from backend.models import Point, Zone
from backend.scenarios import (
    base_scenario,
    activar_zona,
    desactivar_zona,
    modificar_radio_zona,
    actualizar_objeto,
    agregar_objeto_existente,
)
from backend.restrictions.geometry import distancia_angular
from backend.restrictions.validator import validar_objetos_existentes, validar_satelite

def test_dos_objetos_existentes_configuracion():
    """Verifica el registro de los dos objetos existentes con parámetros oficiales."""
    s = base_scenario()
    objects = {z.name: z for z in s.zones if getattr(z, 'kind', 'debris') == 'object'}
    
    assert "Objeto A" in objects
    assert "Objeto B" in objects
    
    # Objeto A: lat 10°, lon 45°, radio de exclusión 5°
    obj_a = objects["Objeto A"]
    assert obj_a.lat == pytest.approx(10.0)
    assert obj_a.lon == pytest.approx(45.0)
    assert obj_a.radius_deg == pytest.approx(5.0)
    assert obj_a.active is True
    assert obj_a.kind == 'object'
    
    # Objeto B: lat -15°, lon 110°, radio de exclusión 5°
    obj_b = objects["Objeto B"]
    assert obj_b.lat == pytest.approx(-15.0)
    assert obj_b.lon == pytest.approx(110.0)
    assert obj_b.radius_deg == pytest.approx(5.0)
    assert obj_b.active is True
    assert obj_b.kind == 'object'

def test_separacion_angular_y_exclusion_objeto_a():
    """Evalúa la detección de invasión dentro y sobre el radio de exclusión del Objeto A."""
    s = base_scenario()
    
    # Satélite en el centro del Objeto A: violación
    centro = Point(lat=10.0, lon=45.0)
    v_centro = validar_objetos_existentes(centro, s.zones, satelite_idx=1)
    assert len(v_centro) == 1
    assert v_centro[0].tipo == "objeto_existente"
    assert v_centro[0].nombre == "Objeto A"
    assert v_centro[0].distancia_deg == pytest.approx(0.0, abs=1e-3)
    assert v_centro[0].radio_limite_deg == pytest.approx(5.0)
    
    # Satélite a 5.0° (sobre el límite de exclusión): violación
    en_limite = Point(lat=15.0, lon=45.0)
    assert distancia_angular([15.0, 45.0], [10.0, 45.0]) == pytest.approx(5.0)
    v_limite = validar_objetos_existentes(en_limite, s.zones, satelite_idx=1)
    assert len(v_limite) == 1
    assert v_limite[0].nombre == "Objeto A"
    
    # Satélite a 5.1° (fuera del radio de exclusión): válido
    fuera = Point(lat=15.1, lon=45.0)
    v_fuera = validar_objetos_existentes(fuera, s.zones, satelite_idx=1)
    assert len(v_fuera) == 0

def test_separacion_angular_y_exclusion_objeto_b():
    """Evalúa la detección de invasión del Objeto B y su diferenciación respecto a A."""
    s = base_scenario()
    
    # Satélite en el centro del Objeto B
    centro_b = Point(lat=-15.0, lon=110.0)
    v_b = validar_objetos_existentes(centro_b, s.zones, satelite_idx=2)
    assert len(v_b) == 1
    assert v_b[0].tipo == "objeto_existente"
    assert v_b[0].nombre == "Objeto B"
    assert "Objeto A" not in [v.nombre for v in v_b]

def test_modificar_radio_exclusion_objetos():
    """Permite modificar el radio de exclusión de los objetos existentes."""
    s = base_scenario()
    punto = Point(lat=17.0, lon=45.0)  # Distancia a Objeto A = 7°
    
    # Con radio base 5°, está libre
    assert len(validar_objetos_existentes(punto, s.zones)) == 0
    
    # Aumentar radio de exclusión a 8°
    modificar_radio_zona(s, "Objeto A", 8.0)
    v_expandido = validar_objetos_existentes(punto, s.zones)
    assert len(v_expandido) == 1
    assert v_expandido[0].nombre == "Objeto A"
    assert v_expandido[0].radio_limite_deg == pytest.approx(8.0)

def test_actualizar_posicion_objeto_existente():
    """Permite reubicar o actualizar parámetros de un objeto existente."""
    s = base_scenario()
    # Reubicar Objeto A a lat=20, lon=50
    ok = actualizar_objeto(s, "Objeto A", lat=20.0, lon=50.0, radio_exclusion_deg=6.0)
    assert ok is True
    
    # Verificar que el punto viejo ahora está libre
    punto_viejo = Point(lat=10.0, lon=45.0)
    assert len(validar_objetos_existentes(punto_viejo, s.zones)) == 0
    
    # Verificar que el nuevo punto detecta la exclusión
    punto_nuevo = Point(lat=20.0, lon=50.0)
    v_nuevo = validar_objetos_existentes(punto_nuevo, s.zones)
    assert len(v_nuevo) == 1
    assert v_nuevo[0].nombre == "Objeto A"

def test_independencia_entre_objetos_y_zonas_restringidas():
    """Verifica que los objetos y las zonas restringidas se categoricen y validen independientemente."""
    s = base_scenario()
    
    # Satélite en Atlántico Norte (zona restringida): debe violar zona, NO objeto
    sat_zona = Point(lat=45.0, lon=-35.0)
    violaciones_sat = validar_satelite(sat_zona, s, satelite_idx=1)
    tipos = [v.tipo for v in violaciones_sat]
    assert "zona_restringida" in tipos
    assert "objeto_existente" not in tipos
    
    # Satélite en Objeto B: debe violar objeto, NO zona
    sat_obj = Point(lat=-15.0, lon=110.0)
    violaciones_obj = validar_satelite(sat_obj, s, satelite_idx=2)
    tipos_obj = [v.tipo for v in violaciones_obj]
    assert "objeto_existente" in tipos_obj
    assert "zona_restringida" not in tipos_obj

def test_incorporar_nuevo_objeto_existente():
    """Permite incorporar nuevos objetos ocupando posición sin alterar la lógica existente."""
    s = base_scenario()
    nuevo = agregar_objeto_existente(s, "Estación Espacial Alfa", lat=0.0, lon=0.0, radio_exclusion_deg=4.0)
    assert nuevo.kind == "object"
    assert nuevo.name == "Estación Espacial Alfa"
    
    v = validar_objetos_existentes(Point(lat=0.0, lon=0.0), s.zones)
    assert len(v) == 1
    assert v[0].tipo == "objeto_existente"
    assert v[0].nombre == "Estación Espacial Alfa"
