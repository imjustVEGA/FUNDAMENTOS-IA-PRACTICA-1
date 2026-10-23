"""Pruebas unitarias de las tres zonas restringidas por desechos espaciales (Integrante 3: Owen)."""
import pytest
import numpy as np
from backend.models import Point, Zone
from backend.scenarios import (
    base_scenario,
    activar_zona,
    desactivar_zona,
    modificar_radio_zona,
    agregar_zona_restringida,
)
from backend.restrictions.geometry import distancia_angular, esta_en_o_sobre_limite
from backend.restrictions.validator import validar_zonas_restringidas, is_valid_point

def test_tres_zonas_obligatorias_configuracion():
    """Verifica que el escenario base incluya las tres zonas obligatorias con parámetros exactos."""
    s = base_scenario()
    debris_zones = {z.name: z for z in s.zones if getattr(z, 'kind', 'debris') == 'debris'}
    
    assert "Atlántico Norte" in debris_zones
    assert "Pacífico Sur" in debris_zones
    assert "Polar norte" in debris_zones
    
    # Atlántico Norte: 45°, -35°, 12°
    atlantico = debris_zones["Atlántico Norte"]
    assert atlantico.lat == pytest.approx(45.0)
    assert atlantico.lon == pytest.approx(-35.0)
    assert atlantico.radius_deg == pytest.approx(12.0)
    assert atlantico.active is True
    
    # Pacífico Sur: -30°, -120°, 10°
    pacifico = debris_zones["Pacífico Sur"]
    assert pacifico.lat == pytest.approx(-30.0)
    assert pacifico.lon == pytest.approx(-120.0)
    assert pacifico.radius_deg == pytest.approx(10.0)
    assert pacifico.active is True
    
    # Polar norte: 78°, 30°, 8°
    polar = debris_zones["Polar norte"]
    assert polar.lat == pytest.approx(78.0)
    assert polar.lon == pytest.approx(30.0)
    assert polar.radius_deg == pytest.approx(8.0)
    assert polar.active is True

def test_satelite_fuera_de_zonas_restringidas():
    """Un satélite en un área libre no debe generar violaciones de zonas restringidas."""
    s = base_scenario()
    satelite_libre = Point(lat=0.0, lon=0.0)
    violaciones = validar_zonas_restringidas(satelite_libre, s.zones, satelite_idx=1)
    assert len(violaciones) == 0

def test_satelite_dentro_de_cada_zona_restringida():
    """Un satélite en el centro geográfico de cada zona debe ser rechazado."""
    s = base_scenario()
    
    # 1. Dentro de Atlántico Norte
    v_atlantico = validar_zonas_restringidas(Point(lat=45.0, lon=-35.0), s.zones, satelite_idx=1)
    assert len(v_atlantico) == 1
    assert v_atlantico[0].tipo == "zona_restringida"
    assert v_atlantico[0].nombre == "Atlántico Norte"
    assert v_atlantico[0].distancia_deg == pytest.approx(0.0, abs=1e-3)
    
    # 2. Dentro de Pacífico Sur
    v_pacifico = validar_zonas_restringidas(Point(lat=-30.0, lon=-120.0), s.zones, satelite_idx=2)
    assert len(v_pacifico) == 1
    assert v_pacifico[0].tipo == "zona_restringida"
    assert v_pacifico[0].nombre == "Pacífico Sur"
    
    # 3. Dentro de Polar norte
    v_polar = validar_zonas_restringidas(Point(lat=78.0, lon=30.0), s.zones, satelite_idx=3)
    assert len(v_polar) == 1
    assert v_polar[0].tipo == "zona_restringida"
    assert v_polar[0].nombre == "Polar norte"

def test_satelite_exactamente_en_el_limite_de_exclusion():
    """El límite (distancia == radio) debe ser considerado violación; puntos a radio + epsilon deben ser válidos."""
    s = base_scenario()
    # Atlántico Norte: lat 45, lon -35, radio 12.
    # Desplazamiento de exactamente 12° en latitud: (45 + 12 = 57, -35)
    punto_en_frontera = Point(lat=57.0, lon=-35.0)
    assert distancia_angular([57.0, -35.0], [45.0, -35.0]) == pytest.approx(12.0)
    
    # En el límite: violación
    v_frontera = validar_zonas_restringidas(punto_en_frontera, s.zones, satelite_idx=1)
    assert len(v_frontera) == 1
    assert v_frontera[0].nombre == "Atlántico Norte"
    
    # Apenas fuera de la frontera: 12.01° -> válido
    punto_fuera_frontera = Point(lat=57.01, lon=-35.0)
    v_fuera = validar_zonas_restringidas(punto_fuera_frontera, s.zones, satelite_idx=1)
    assert len(v_fuera) == 0

def test_activacion_y_desactivacion_de_zonas():
    """Permite activar y desactivar cada zona; si está inactiva no debe registrar violaciones."""
    s = base_scenario()
    posicion_atlantico = Point(lat=45.0, lon=-35.0)
    
    # Activa inicialmente
    assert len(validar_zonas_restringidas(posicion_atlantico, s.zones)) == 1
    
    # Desactivar
    desactivar_zona(s, "Atlántico Norte")
    assert len(validar_zonas_restringidas(posicion_atlantico, s.zones)) == 0
    
    # Reactivar
    activar_zona(s, "Atlántico Norte")
    assert len(validar_zonas_restringidas(posicion_atlantico, s.zones)) == 1

def test_modificar_radio_angular_de_zona():
    """Permite modificar el radio angular de una zona y altera la frontera de exclusión."""
    s = base_scenario()
    # Punto a 15° de Atlántico Norte (45 + 15 = 60, -35)
    punto = Point(lat=60.0, lon=-35.0)
    
    # Con radio base 12°, está libre
    assert len(validar_zonas_restringidas(punto, s.zones)) == 0
    
    # Aumentar radio a 16°
    modificar_radio_zona(s, "Atlántico Norte", 16.0)
    # Ahora debe invadir la zona
    assert len(validar_zonas_restringidas(punto, s.zones)) == 1
    
    # Reducir radio a 5°
    modificar_radio_zona(s, "Atlántico Norte", 5.0)
    assert len(validar_zonas_restringidas(punto, s.zones)) == 0

def test_incorporar_nuevas_zonas_sin_alterar_logica():
    """Permite añadir nuevas zonas restringidas dinámicamente."""
    s = base_scenario()
    punto = Point(lat=10.0, lon=-10.0)
    assert len(validar_zonas_restringidas(punto, s.zones)) == 0
    
    # Añadir nueva zona restringida
    nueva = agregar_zona_restringida(s, "Zona Sahara Debris", lat=10.0, lon=-10.0, radio_deg=6.0)
    assert nueva.name == "Zona Sahara Debris"
    assert nueva.kind == "debris"
    
    # Ahora debe detectar la nueva zona
    violaciones = validar_zonas_restringidas(punto, s.zones)
    assert len(violaciones) == 1
    assert violaciones[0].nombre == "Zona Sahara Debris"

def test_geometria_esferica_polar_y_antimeridiano():
    """Valida que la distancia esférica y zonas respeten la geometría de la esfera en polos y antimeridiano."""
    s = base_scenario()
    # Polar norte: lat 78°, lon 30°, radio 8°.
    # Polo Norte geográfico (lat 90°, lon 30°): distancia = 90 - 78 = 12° -> fuera de radio 8°
    assert len(validar_zonas_restringidas(Point(lat=90.0, lon=30.0), s.zones)) == 0
    
    # Punto a lat 82°, lon 30°: distancia = 4° -> dentro de Polar norte (radio 8°)
    v = validar_zonas_restringidas(Point(lat=82.0, lon=30.0), s.zones)
    assert len(v) == 1
    assert v[0].nombre == "Polar norte"
    
    # Cruce del antimeridiano con zona en lon=179°
    agregar_zona_restringida(s, "Zona Antimeridiano", lat=0.0, lon=179.0, radio_deg=5.0)
    # Punto en lon=-179°: distancia angular a lon 179° en el ecuador es 2° (cruzando el antimeridiano)
    punto_antimeridiano = Point(lat=0.0, lon=-179.0)
    v_anti = validar_zonas_restringidas(punto_antimeridiano, s.zones)
    assert any(x.nombre == "Zona Antimeridiano" for x in v_anti)
