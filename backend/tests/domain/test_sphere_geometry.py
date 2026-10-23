import math

import numpy as np
import pytest

from app.domain.sphere_geometry import (
    R_TIERRA_KM,
    distancia_haversine_km,
    latlon_a_xyz,
    normalizar_longitud,
    punto_dentro_de_disco,
    validar_coordenada,
)


def test_distancia_de_un_punto_a_si_mismo_es_cero():
    assert distancia_haversine_km(12.3, -45.6, 12.3, -45.6) == pytest.approx(0.0)


def test_distancia_polo_a_polo_es_mitad_de_la_circunferencia():
    assert distancia_haversine_km(90, 0, -90, 0) == pytest.approx(math.pi * R_TIERRA_KM)


def test_haversine_cruza_el_antimeridiano_por_el_arco_corto():
    esperado = math.radians(1.0) * R_TIERRA_KM
    assert distancia_haversine_km(0, 179.5, 0, -179.5) == pytest.approx(esperado)


@pytest.mark.parametrize(
    ("longitud", "esperado"),
    [(181, -179), (-181, 179), (360, 0)],
)
def test_normalizar_longitud(longitud, esperado):
    assert normalizar_longitud(longitud) == pytest.approx(esperado)


@pytest.mark.parametrize(
    ("latitud", "longitud"),
    [(91, 0), (-91, 0), (0, 181), (0, -181), (math.nan, 0), (0, math.nan)],
)
def test_validar_coordenada_rechaza_rangos_invalidos_y_nan(latitud, longitud):
    with pytest.raises(ValueError):
        validar_coordenada(latitud, longitud)


def test_punto_dentro_de_disco_cubre_interior_borde_y_exterior():
    radio = 100.0
    borde_lon = math.degrees(radio / R_TIERRA_KM)
    assert punto_dentro_de_disco(0, 0.5 * borde_lon, 0, 0, radio)
    assert punto_dentro_de_disco(0, borde_lon, 0, 0, radio)
    assert not punto_dentro_de_disco(0, 1.1 * borde_lon, 0, 0, radio)


def test_latlon_a_xyz_conserva_la_norma_del_radio():
    radio = 42.0
    xyz = latlon_a_xyz(np.array([0.0, 45.0]), np.array([0.0, 120.0]), radio)
    assert xyz.shape == (2, 3)
    np.testing.assert_allclose(np.linalg.norm(xyz, axis=-1), radio)
