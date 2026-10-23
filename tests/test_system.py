import numpy as np
import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient
from backend.geometry import angular, disk_samples, move
from backend.models import Point, Parameters, EvaluationRequest, Run, Zone
from backend.scenarios import base_scenario
from backend.constraints import valid_point
from backend.coverage import Evaluator
from backend.evolution import optimize
from backend.api import app

@pytest.mark.parametrize('a,b,expected',[
    ([0,179],[0,-179],2),([90,0],[90,170],0),([0,0],[0,180],180),
    ([0,0],[90,0],90),([-90,-50],[-90,140],0)])
def test_distances(a,b,expected):
    assert angular(a,b)==pytest.approx(expected,abs=1e-8)

def test_samples_uniform_reproducible_inside_disk():
    a=disk_samples(90,179,300,128)
    assert np.array_equal(a,disk_samples(90,179,300,128))
    assert np.max(angular(a,[90,179]))<=np.degrees(300/6371)
    assert np.all(np.isfinite(a))

def test_mutation_poles():
    for lat in [-90,90]:
        p=move([lat,180],50,50)
        Point(lat=p[0],lon=p[1])

def test_union_and_surface_not_center():
    s=base_scenario()
    s.zones=[]
    c=np.array([[r.lat,r.lon] for r in s.regions]+[[0,40],[0,60]])
    assert Evaluator(s).evaluate(c).fitness==100
    c[:]=[s.regions[0].lat,s.regions[0].lon]
    s.footprint_km=50
    e=Evaluator(s).evaluate(c)
    assert 0 < e.coverage[0].fraction < .8
    assert e.coverage[1].fraction==0
    assert e.status=='valid_insufficient'

def test_restrictions_boundaries_and_disable():
    s=base_scenario()
    for z in s.zones:
        assert not valid_point([z.lat,z.lon],s)
    s.zones=[Zone(name='test',lat=0,lon=0,radius_deg=5)]
    assert not valid_point([0,5],s)
    assert valid_point([0,5.01],s)
    s.zones[0].active=False
    assert valid_point([0,0],s)

@pytest.fixture(scope='module')
def run(): return optimize(base_scenario(),Parameters(population=24,generations=20))

def test_evolution_feasibility_elitism(run):
    assert run.status=='success'
    assert len(run.final)==8
    assert all(x.valid_count==24 for x in run.history)
    assert all(a.best<=b.best for a,b in zip(run.history,run.history[1:]))
    assert run.final_evaluation.fitness>=run.initial_evaluation.fitness
    assert all(valid_point([p.lat,p.lon],run.scenario) for p in run.final)
    assert len(run.history)==21

def test_reproduction_serialization(run):
    assert run.model_dump()==optimize(run.scenario,run.parameters).model_dump()
    assert Run.model_validate_json(run.model_dump_json())==run

def test_impossible_and_bounded_failure():
    s=base_scenario()
    s.zones.append(Zone(name='Toda la esfera',lat=0,lon=0,radius_deg=180))
    r=optimize(s,Parameters())
    assert r.status=='no_feasible_found' and r.final is None
    s.zones[-1].radius_deg=179.999999
    r=optimize(s,Parameters(attempts=1))
    assert r.status=='no_feasible_found'

def test_validation():
    with pytest.raises(ValidationError): Point(lat=float('nan'),lon=0)
    with pytest.raises(ValidationError): Parameters(elite=80)
    with pytest.raises(ValidationError): EvaluationRequest(configuration=[Point(lat=0,lon=0)],scenario=base_scenario())

def test_api(run):
    client=TestClient(app)
    assert client.get('/api/scenario').status_code==200
    body={'configuration':[p.model_dump() for p in run.final],'scenario':run.scenario.model_dump()}
    assert client.post('/api/validate',json=body).json()['valid']
    altered=run.scenario.model_copy(deep=True)
    altered.zones.append(Zone(name='Nuevo bloqueo',lat=run.final[0].lat,lon=run.final[0].lon,radius_deg=1))
    response=client.post('/api/compare',json={**body,'previous_scenario':body['scenario'],'scenario':altered.model_dump()})
    assert response.json()['before']['valid'] and not response.json()['after']['valid']
    assert client.post('/api/evaluate',json={**body,'configuration':[]}).status_code==422
    response=client.post('/api/optimize',json={'scenario':body['scenario'],'parameters':{'population':8,'elite':1,'generations':1}})
    assert response.status_code==200 and len(response.json()['history'])==2
    run_id=response.json()['run_id']
    assert client.get(f'/api/runs/{run_id}').json()==response.json()
    assert len(client.get(f'/api/runs/{run_id}/history').json())==2
    assert len(client.get(f'/api/runs/{run_id}/configurations').json()['final'])==8
    assert client.get('/api/runs/nonexistent').status_code==404
