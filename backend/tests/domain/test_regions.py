import numpy as np
import pytest

from app.domain.regions import (
    OBJETOS_OCUPADOS_BASE,
    REGIONES_BASE,
    ZONAS_RESTRINGIDAS_BASE,
    muestrear_region,
    precomputar_muestras,
    satelite_en_zona,
)
from app.domain.sphere_geometry import RADIO_REGION_KM, distancia_haversine_km


def test_datos_base_tienen_regiones_prioridades_y_discos_del_enunciado():
    assert len(REGIONES_BASE) == 6
    assert [region.prioridad for region in REGIONES_BASE] == [
        "alta",
        "alta",
        "media",
        "media",
        "media",
        "normal",
    ]
    assert [region.peso for region in REGIONES_BASE] == [3, 3, 2, 2, 2, 1]
    assert len(ZONAS_RESTRINGIDAS_BASE) == 3
    assert len(OBJETOS_OCUPADOS_BASE) == 2


def test_muestreo_es_reproducible_con_la_misma_semilla():
    primera = muestrear_region(REGIONES_BASE[0], 200, 17)
    segunda = muestrear_region(REGIONES_BASE[0], 200, 17)
    np.testing.assert_array_equal(primera[0], segunda[0])
    np.testing.assert_array_equal(primera[1], segunda[1])


@pytest.mark.parametrize("region", REGIONES_BASE)
def test_muestras_estan_dentro_del_radio_de_300_km(region):
    latitudes, longitudes = region.muestras_lat, region.muestras_lon
    distancias = distancia_haversine_km(latitudes, longitudes, region.lat, region.lon)
    assert np.all(distancias <= RADIO_REGION_KM + 1e-8)


def test_satelite_en_zona_detecta_polo_norte_y_objeto_a():
    assert satelite_en_zona(78, 30, ZONAS_RESTRINGIDAS_BASE[2])
    objeto_a = OBJETOS_OCUPADOS_BASE[0]
    assert satelite_en_zona(objeto_a.lat, objeto_a.lon, objeto_a)


def test_precomputar_muestras_acepta_semilla_y_tamano():
    regiones = precomputar_muestras(REGIONES_BASE, n=12, semilla=4)
    assert all(region.muestras_lat.size == 12 for region in regiones)
