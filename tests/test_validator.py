"""Pruebas unitarias del validador de configuraciones y restricciones (Integrante 3: Owen)."""
import pytest
import numpy as np
from fastapi.testclient import TestClient
from backend.models import Point, Scenario, EvaluationRequest
from backend.scenarios import base_scenario
from backend.restrictions.validator import (
    validar_configuracion,
    validar_satelite,
    validar_coordenadas,
)
from backend.restrictions.geometry import distancia_angular
from backend.api import app

@pytest.fixture
def configuracion_valida():
    """Retorna 8 satélites situados en coordenadas sin restricciones activas."""
    return [
        Point(lat=0.0, lon=0.0),
        Point(lat=20.0, lon=-80.0),
        Point(lat=-20.0, lon=-50.0),
        Point(lat=30.0, lon=-100.0),
        Point(lat=-10.0, lon=20.0),
        Point(lat=50.0, lon=100.0),
        Point(lat=-50.0, lon=80.0),
        Point(lat=10.0, lon=-140.0),
    ]

def test_configuracion_ocho_satelites_completamente_valida(configuracion_valida):
    """Una constelación de exactamente 8 satélites en posiciones libres debe ser válida."""
    s = base_scenario()
    res = validar_configuracion(configuracion_valida, s)
    
    assert res.valida is True
    assert res.total_satelites == 8
    assert res.total_violaciones == 0
    assert len(res.violaciones) == 0
    assert "Configuración válida" in res.resumen

def test_configuracion_con_satelites_invalidos(configuracion_valida):
    """Detecta violaciones específicas con información estructurada."""
    s = base_scenario()
    # Modificamos el satélite 3 para invadir Atlántico Norte
    configuracion_valida[2] = Point(lat=45.0, lon=-35.0)
    # Modificamos el satélite 7 para invadir Objeto B
    configuracion_valida[6] = Point(lat=-15.0, lon=110.0)
    
    res = validar_configuracion(configuracion_valida, s)
    
    assert res.valida is False
    assert res.total_satelites == 8
    assert res.total_violaciones == 2
    
    sat_indices = [v.satelite for v in res.violaciones]
    assert 3 in sat_indices
    assert 7 in sat_indices
    
    v3 = next(v for v in res.violaciones if v.satelite == 3)
    assert v3.tipo == "zona_restringida"
    assert v3.nombre == "Atlántico Norte"
    
    v7 = next(v for v in res.violaciones if v.satelite == 7)
    assert v7.tipo == "objeto_existente"
    assert v7.nombre == "Objeto B"

def test_cantidad_incorrecta_de_satelites():
    """Rechaza configuraciones con diferente cantidad a los 8 satélites requeridos."""
    s = base_scenario()
    
    # 5 satélites
    pocos = [Point(lat=0.0, lon=float(i * 10)) for i in range(5)]
    res_pocos = validar_configuracion(pocos, s)
    assert res_pocos.valida is False
    assert any(v.tipo == "cantidad_invalida" for v in res_pocos.violaciones)
    assert res_pocos.total_satelites == 5
    
    # 10 satélites
    muchos = [Point(lat=0.0, lon=float(i * 10)) for i in range(10)]
    res_muchos = validar_configuracion(muchos, s)
    assert res_muchos.valida is False
    assert any(v.tipo == "cantidad_invalida" for v in res_muchos.violaciones)
    assert res_muchos.total_satelites == 10

def test_coordenadas_fuera_de_rango():
    """Detecta latitudes y longitudes fuera de los límites esféricos."""
    # Latitud > 90
    v_lat_pos = validar_coordenadas({"lat": 95.0, "lon": 0.0}, satelite_idx=1)
    assert len(v_lat_pos) == 1
    assert v_lat_pos[0].tipo == "coordenadas_invalidas"
    assert "[-90°, 90°]" in v_lat_pos[0].descripcion
    
    # Latitud < -90
    v_lat_neg = validar_coordenadas({"lat": -91.0, "lon": 0.0}, satelite_idx=2)
    assert len(v_lat_neg) == 1
    assert v_lat_neg[0].tipo == "coordenadas_invalidas"
    
    # Longitud > 180
    v_lon_pos = validar_coordenadas({"lat": 0.0, "lon": 185.0}, satelite_idx=3)
    assert len(v_lon_pos) == 1
    assert v_lon_pos[0].tipo == "coordenadas_invalidas"
    assert "[-180°, 180°]" in v_lon_pos[0].descripcion
    
    # Longitud < -180
    v_lon_neg = validar_coordenadas({"lat": 0.0, "lon": -180.5}, satelite_idx=4)
    assert len(v_lon_neg) == 1
    assert v_lon_neg[0].tipo == "coordenadas_invalidas"

def test_coordenadas_no_finitas_nan_inf():
    """Rechaza coordenadas no numéricas o infinitas sin provocar caídas del sistema."""
    v_nan = validar_coordenadas({"lat": float('nan'), "lon": 0.0}, satelite_idx=1)
    assert len(v_nan) == 1
    assert v_nan[0].tipo == "coordenadas_invalidas"
    assert "NaN o Infinito" in v_nan[0].descripcion
    
    v_inf = validar_coordenadas({"lat": 0.0, "lon": float('inf')}, satelite_idx=2)
    assert len(v_inf) == 1
    assert v_inf[0].tipo == "coordenadas_invalidas"

def test_calculo_angular_polos_y_antimeridiano():
    """Comprueba la exactitud de distancia_angular en los polos y antimeridiano."""
    # En el polo norte (90° latitud), la longitud es degenerada: distancia entre dos puntos a lat 90 es 0°
    assert distancia_angular([90.0, 0.0], [90.0, 150.0]) == pytest.approx(0.0, abs=1e-8)
    
    # Distancia polo norte a polo sur es 180°
    assert distancia_angular([90.0, 0.0], [-90.0, 0.0]) == pytest.approx(180.0, abs=1e-8)
    
    # Antimeridiano: longitud 179° y -179° en el ecuador distan 2°
    assert distancia_angular([0.0, 179.0], [0.0, -179.0]) == pytest.approx(2.0, abs=1e-8)
    
    # Longitud 180° y -180° representan el mismo meridiano
    assert distancia_angular([0.0, 180.0], [0.0, -180.0]) == pytest.approx(0.0, abs=1e-8)

def test_distincion_entre_configuracion_invalida_y_cobertura_insuficiente(configuracion_valida):
    """El validador declara válida una configuración factible aunque su cobertura sea nula o parcial."""
    s = base_scenario()
    # Los 8 satélites están concentrados en el Polo Sur (lat=-85), lejos de las regiones terrestres
    concentrados = [Point(lat=-85.0, lon=float(i * 10)) for i in range(8)]
    
    res = validar_configuracion(concentrados, s)
    # Debe ser válida en cuanto a restricciones aunque su cobertura terrestre sea mínima
    assert res.valida is True
    assert res.total_violaciones == 0

def test_api_rest_validador_restricciones(configuracion_valida):
    """Comprueba el endpoint REST /api/restrictions/validate con TestClient de FastAPI."""
    client = TestClient(app)
    s = base_scenario()
    
    # Configuración válida
    body = {
        "configuration": [p.model_dump() for p in configuracion_valida],
        "scenario": s.model_dump()
    }
    r = client.post("/api/restrictions/validate", json=body)
    assert r.status_code == 200
    data = r.json()
    assert data["valida"] is True
    assert data["total_violaciones"] == 0
    
    # Invasión deliberada
    body["configuration"][0] = {"lat": 45.0, "lon": -35.0}  # Atlántico Norte
    r_inv = client.post("/api/restrictions/validate", json=body)
    assert r_inv.status_code == 200
    data_inv = r_inv.json()
    assert data_inv["valida"] is False
    assert data_inv["total_violaciones"] >= 1
    assert data_inv["violaciones"][0]["tipo"] == "zona_restringida"
    assert data_inv["violaciones"][0]["nombre"] == "Atlántico Norte"
