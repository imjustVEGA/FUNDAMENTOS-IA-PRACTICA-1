"""Pruebas unitarias de escenarios dinámicos y persistencia JSON (Integrante 3: Owen)."""
import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from backend.models import Point, Scenario, Parameters
from backend.scenarios import (
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
)
from backend.restrictions.validator import validar_configuracion
from backend.evolution import optimize
from backend.api import app

@pytest.fixture
def configuracion_base():
    return [
        Point(lat=20.5, lon=-89.0),
        Point(lat=-3.5, lon=-62.0),
        Point(lat=36.8, lon=-119.4),
        Point(lat=15.0, lon=0.0),
        Point(lat=36.0, lon=138.0),
        Point(lat=-25.0, lon=133.0),
        Point(lat=0.0, lon=30.0),
        Point(lat=-45.0, lon=0.0),
    ]

def test_guardar_y_recuperar_escenario_json(tmp_path):
    """Permite serializar un escenario a JSON y recuperarlo sin pérdida de fidelidad."""
    s = base_scenario()
    s.name = "Escenario de Prueba JSON"
    modificar_prioridad_region(s, "Península de Yucatán", 15.0)
    agregar_zona_restringida(s, "Zona Nueva", lat=12.0, lon=34.0, radio_deg=7.5)
    
    archivo_destino = tmp_path / "escenario_test.json"
    guardar_escenario_json(s, archivo_destino)
    assert archivo_destino.exists()
    
    recuperado = cargar_escenario_json(archivo_destino)
    assert recuperado.name == "Escenario de Prueba JSON"
    assert len(recuperado.zones) == len(s.zones)
    assert recuperado.regions[0].weight == pytest.approx(15.0)
    
    zona_nueva = next(z for z in recuperado.zones if z.name == "Zona Nueva")
    assert zona_nueva.lat == pytest.approx(12.0)
    assert zona_nueva.radius_deg == pytest.approx(7.5)

def test_modificar_prioridad_de_regiones():
    """Permite ajustar los pesos de las regiones terrestres objetivo."""
    s = base_scenario()
    ok = modificar_prioridad_region(s, "Amazonía brasileña", 10.0)
    assert ok is True
    
    region = next(r for r in s.regions if r.name == "Amazonía brasileña")
    assert region.weight == pytest.approx(10.0)
    
    with pytest.raises(ValueError):
        modificar_prioridad_region(s, "Amazonía brasileña", -5.0)
    with pytest.raises(ValueError):
        modificar_prioridad_region(s, "Amazonía brasileña", 150.0)

def test_reevaluar_configuracion_anterior_al_cambiar_condiciones(configuracion_base):
    """Comprueba la validez de una solución existente al modificar o agregar restricciones."""
    s_inicial = base_scenario()
    
    # 1. En el escenario inicial, la configuración es válida
    res_inicial = validar_configuracion(configuracion_base, s_inicial)
    assert res_inicial.valida is True
    
    # 2. Modificamos el escenario agregando una restricción sobre la posición del satélite 1 (Yucatán: 20.5, -89)
    s_modificado = s_inicial.model_copy(deep=True)
    s_modificado.name = "Escenario con Bloqueo Sobrevenido"
    agregar_zona_restringida(s_modificado, "Bloqueo Yucatán", lat=20.5, lon=-89.0, radio_deg=5.0)
    
    # 3. Reevaluar la solución previa bajo las nuevas condiciones
    comparacion = reevaluar_configuracion_anterior(configuracion_base, s_inicial, s_modificado)
    
    assert comparacion.anterior_valida is True
    assert comparacion.actual_valida is False
    assert comparacion.cambio_validez is True
    assert "Bloqueo Yucatán" in comparacion.detalles
    assert comparacion.resultado_actual.total_violaciones >= 1

def test_actualizar_escenario_y_reoptimizar_con_algoritmo_genetico():
    """Proporciona el escenario actualizado al algoritmo genético para ejecutar nuevamente la optimización."""
    s = base_scenario()
    # Desactivar Atlántico Norte y aumentar radio de Polar norte
    desactivar_zona(s, "Atlántico Norte")
    modificar_radio_zona(s, "Polar norte", 12.0)
    
    # Ejecutar una optimización rápida (población pequeña y pocas generaciones para prueba ágil)
    p = Parameters(population=12, generations=3, seed=42)
    resultado = optimize(s, p)
    
    assert resultado.status == "success"
    assert len(resultado.final) == 8
    
    # La solución final generada debe cumplir el escenario modificado
    res_val = validar_configuracion(resultado.final, s)
    assert res_val.valida is True
    assert res_val.total_violaciones == 0

def test_api_rest_reevaluacion_y_comparacion(configuracion_base):
    """Prueba el endpoint /api/restrictions/compare con FastAPI TestClient."""
    client = TestClient(app)
    s_base = base_scenario()
    s_nuevo = s_base.model_copy(deep=True)
    agregar_zona_restringida(s_nuevo, "Nube Debris Nueva", lat=configuracion_base[0].lat, lon=configuracion_base[0].lon, radio_deg=4.0)
    
    payload = {
        "configuration": [p.model_dump() for p in configuracion_base],
        "previous_scenario": s_base.model_dump(),
        "scenario": s_nuevo.model_dump()
    }
    r = client.post("/api/restrictions/compare", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["anterior_valida"] is True
    assert data["actual_valida"] is False
    assert data["cambio_validez"] is True
    assert "Nube Debris Nueva" in data["detalles"]
