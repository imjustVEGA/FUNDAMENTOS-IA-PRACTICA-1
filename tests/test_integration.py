import json
from pathlib import Path
import numpy as np
import pytest
from fastapi.testclient import TestClient
from backend.api import app
from backend.geometry import disk_samples, vectors, angular
from backend.coverage import Evaluator
from backend.scenarios import base_scenario, actualizar_objeto
from backend.models import Parameters, Run, Zone
from backend.evolution import optimize
from backend.restrictions.validator import validar_coordenadas, validar_configuracion
from backend.app.domain.regions import RegionInteres, muestrear_region
from backend.app.domain.coverage import cobertura_por_region, fitness_por_cobertura

@pytest.mark.parametrize('lat',[90,-90])
def test_polar_samples_cover_both_tangent_directions(lat):
    for p in [disk_samples(lat,179,300,128),np.column_stack(muestrear_region(RegionInteres('Polar',lat,179,'alta'),1000,42))]:
        u=vectors(p)
        eigen=np.linalg.eigvalsh(np.cov(u[:,:2].T))
        assert eigen[0]/eigen[1]>.75
        assert np.max(angular(p,[lat,179])) <= np.degrees(300/6371)+1e-8

def test_domain_coverage_and_service_match_on_identical_samples():
    s=base_scenario()
    c=np.array([[r.lat+5,r.lon] for r in s.regions]+[[0,20],[0,70]])
    domain=[]
    for r in s.regions:
        p=disk_samples(r.lat,r.lon,r.radius_km,s.samples)
        domain.append(RegionInteres(r.name,r.lat,r.lon,'normal',peso=r.weight,muestras_lat=p[:,0],muestras_lon=p[:,1]))
    results=cobertura_por_region(c,domain,s.footprint_km)
    evaluation=Evaluator(s).evaluate(c)
    assert [r.fraccion for r in results]==[r.fraction for r in evaluation.coverage]
    assert fitness_por_cobertura(results)==pytest.approx(evaluation.fitness)

@pytest.mark.parametrize('point',[{'lat':'hola','lon':0},{'lat':None,'lon':0},{'lon':0}])
def test_restriction_validator_reports_malformed_coordinates(point):
    assert validar_coordenadas(point)[0].tipo=='coordenadas_invalidas'

def test_object_update_is_validated_and_atomic():
    s=base_scenario()
    original=s.model_dump()
    with pytest.raises(ValueError): actualizar_objeto(s,'Objeto A',lat=95,radio_exclusion_deg=2)
    assert s.model_dump()==original

def test_scenario_catalog_and_new_restriction_endpoints():
    client=TestClient(app)
    catalog=client.get('/api/scenarios').json()
    assert set(catalog)=={'base','reduced','changed','impossible'}
    result=client.post('/api/optimize',json={'scenario':catalog['base'],'parameters':{'population':8,'generations':2,'elite':1}}).json()
    r=Run.model_validate(result)
    assert validar_configuracion(r.final,r.scenario).valida
    body={'configuration':[p.model_dump() for p in r.final],'scenario':catalog['base']}
    detail=client.post('/api/restrictions/validate',json=body).json()
    assert detail['valida']==r.final_evaluation.valid
    assert client.post('/api/optimize',json={'scenario':catalog['impossible']}).json()['status']=='no_feasible_found'

def test_openapi_file_matches_live_contract():
    assert json.loads(Path('frontend/openapi.json').read_text(encoding='utf-8'))==app.openapi()
