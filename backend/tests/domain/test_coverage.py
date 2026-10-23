import numpy as np
import pytest

from app.domain.coverage import (
    CoberturaRegion,
    cobertura_por_region,
    cobertura_ponderada,
    fitness_por_cobertura,
)
from app.domain.regions import REGIONES_BASE
from app.domain.sphere_geometry import UMBRAL_COBERTURA_REGION


def test_ocho_satelites_sobre_centro_cubren_totalmente_la_region():
    region = REGIONES_BASE[0]
    satelites = np.tile([region.lat, region.lon], (8, 1))
    cobertura = cobertura_por_region(satelites, [region])[0]
    assert cobertura.fraccion == 1.0
    assert cobertura.cubierta is True


def test_antipodas_no_cubren_muestras_de_las_regiones():
    satelites = np.array([[-region.lat, region.lon + 180] for region in REGIONES_BASE])
    satelites[:, 1] = (satelites[:, 1] + 180.0) % 360.0 - 180.0
    coberturas = cobertura_por_region(satelites, REGIONES_BASE, 650.0)
    assert all(cobertura.fraccion < 0.05 for cobertura in coberturas)


def test_fitness_esta_acotado_entre_cero_y_cien():
    coberturas = cobertura_por_region(np.empty((0, 2)), REGIONES_BASE)
    resultado = fitness_por_cobertura(coberturas)
    assert 0.0 <= resultado <= 100.0


def test_cobertura_ponderada_respeta_peso_tres_de_region_alta():
    alta, normal = REGIONES_BASE[0], REGIONES_BASE[-1]
    resultado = cobertura_ponderada(
        [
            CoberturaRegion(alta, fraccion=1.0, cubierta=True),
            CoberturaRegion(normal, fraccion=0.0, cubierta=False),
        ]
    )
    assert resultado == pytest.approx(0.75)


def test_satelites_con_forma_incorrecta_lanzan_value_error():
    with pytest.raises(ValueError, match=r"\(N, 2\)"):
        cobertura_por_region(np.zeros((8, 3)), REGIONES_BASE)


def test_union_no_cuenta_dos_veces_un_satellite_repetido():
    region = REGIONES_BASE[0]
    uno = cobertura_por_region(np.array([[region.lat, region.lon]]), [region])[0]
    ocho = cobertura_por_region(
        np.tile([region.lat, region.lon], (8, 1)), [region]
    )[0]
    assert ocho.fraccion == uno.fraccion
    assert uno.cubierta == (uno.fraccion >= UMBRAL_COBERTURA_REGION)
