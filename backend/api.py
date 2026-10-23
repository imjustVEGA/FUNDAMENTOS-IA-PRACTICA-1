from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from collections import OrderedDict
from threading import Lock
from uuid import uuid4
from fastapi.middleware.cors import CORSMiddleware
from .models import Scenario, EvaluationRequest, OptimizeRequest, ComparisonRequest, Comparison, Evaluation, Run, Generation, ConfigurationPair
from .scenarios import base_scenario
from .coverage import Evaluator
from .evolution import optimize

app=FastAPI(title='AstroShield educativo',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173','http://127.0.0.1:5173'],allow_methods=['GET','POST'],allow_headers=['Content-Type'])
results=Path(__file__).resolve().parent.parent/'results'
results.mkdir(exist_ok=True)
app.mount('/evidence',StaticFiles(directory=results),name='evidence')
stored: OrderedDict[str, Run]=OrderedDict()
lock=Lock()

def evaluate(request):
    return Evaluator(request.scenario).evaluate([[p.lat,p.lon] for p in request.configuration])

@app.get('/api/scenario',response_model=Scenario)
def scenario(): return base_scenario()

@app.post('/api/evaluate',response_model=Evaluation)
def evaluation(request: EvaluationRequest): return evaluate(request)

@app.post('/api/validate',response_model=Evaluation)
def validation(request: EvaluationRequest): return evaluate(request)

@app.post('/api/optimize',response_model=Run)
def optimization(request: OptimizeRequest):
    result=optimize(request.scenario,request.parameters)
    result.run_id=uuid4().hex
    with lock:
        stored[result.run_id]=result
        while len(stored)>20: stored.popitem(last=False)
    return result

@app.get('/api/runs/{run_id}',response_model=Run)
def get_run(run_id: str):
    with lock:
        if run_id not in stored: raise HTTPException(404,'Ejecución no disponible en memoria; conserva los resultados mediante la exportación JSON.')
        return stored[run_id]

@app.get('/api/runs/{run_id}/history',response_model=list[Generation])
def history(run_id: str): return get_run(run_id).history

@app.get('/api/runs/{run_id}/configurations',response_model=ConfigurationPair)
def configurations(run_id: str):
    r=get_run(run_id)
    return {'initial':r.initial,'final':r.final}

@app.post('/api/compare',response_model=Comparison)
def compare(request: ComparisonRequest):
    before=Evaluator(request.previous_scenario).evaluate([[p.lat,p.lon] for p in request.configuration])
    return Comparison(before=before,after=evaluate(request))

from .restrictions.models import ValidationResult, ScenarioComparison
from .restrictions.validator import validar_configuracion
from .restrictions.scenarios import reevaluar_configuracion_anterior

@app.post('/api/restrictions/validate', response_model=ValidationResult)
def restriction_validate(request: EvaluationRequest):
    return validar_configuracion(request.configuration, request.scenario)

@app.post('/api/restrictions/compare', response_model=ScenarioComparison)
def restriction_compare(request: ComparisonRequest):
    return reevaluar_configuracion_anterior(request.configuration, request.previous_scenario, request.scenario)

