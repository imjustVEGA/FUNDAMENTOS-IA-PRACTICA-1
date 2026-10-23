import numpy as np
from .models import Point, Run, Generation
from .geometry import uniform_point, move
from .constraints import valid_point
from .coverage import Evaluator
from .restrictions.repair import reparar_configuracion

def points(c):
    return [Point(lat=float(a),lon=float(b)) for a,b in c]

def optimize(scenario, p):
    rng=np.random.default_rng(p.seed)
    evaluator=Evaluator(scenario)
    result=Run(status='no_feasible_found',message='No se encontró una configuración factible dentro del presupuesto; no demuestra imposibilidad.',seed=p.seed,parameters=p,scenario=scenario)
    if any(z.active and z.radius_deg==180 for z in scenario.zones):
        result.message='Una zona activa de 180° excluye toda la esfera: escenario imposible en este modelo.'
        return result

    def repair(c):
        repaired, _ = reparar_configuracion(c, scenario, rng=rng, max_intentos=p.attempts)
        return repaired

    population=[]
    # Referencia uniforme sin conocimiento de regiones.
    for index in range(p.population):
        c=np.array([uniform_point(rng) for _ in range(8)])
        if index and index%2:
            for j in range(8):
                r=scenario.regions[int(rng.integers(6))]
                c[j]=move([r.lat,r.lon],rng.normal(0,9),rng.normal(0,9))
        c=repair(c)
        if c is None: return result
        population.append(c)
    result.initial=points(population[0])
    result.initial_evaluation=evaluator.evaluate(population[0])
    evaluations=[evaluator.evaluate(c) for c in population]
    def key(i): return (evaluations[i].fitness,evaluations[i].separation_deg)
    def record(g):
        i=max(range(p.population),key=key)
        scores=[e.fitness for e in evaluations]
        result.history.append(Generation(generation=g,best=max(scores),mean=float(np.mean(scores)),worst=min(scores),valid_count=sum(e.valid for e in evaluations),best_configuration=points(population[i]),covered_regions=evaluations[i].covered_regions))
    record(0)
    for generation in range(1,p.generations+1):
        order=sorted(range(p.population),key=key,reverse=True)
        children=[population[i].copy() for i in order[:p.elite]]
        def tournament():
            ids=rng.choice(p.population,p.tournament,replace=False)
            return population[max(ids,key=key)]
        for _ in range((p.population-p.elite)*3):
            if len(children)==p.population: break
            a,b=tournament(),tournament()
            child=a.copy()
            if rng.random()<p.crossover:
                mask=rng.random(8)<.5
                child[mask]=b[mask]
            for j in range(8):
                if rng.random()<p.mutation:
                    child[j]=uniform_point(rng) if rng.random()<.15 else move(child[j],rng.normal(0,5),rng.normal(0,5))
            child=repair(child)
            if child is not None: children.append(child)
        # Respaldo factible acotado si fallan reparaciones.
        while len(children)<p.population: children.append(population[order[0]].copy())
        population=children
        evaluations=[evaluator.evaluate(c) for c in population]
        record(generation)
    i=max(range(p.population),key=key)
    result.final=points(population[i])
    result.final_evaluation=evaluations[i]
    assert result.final_evaluation.valid
    result.status='success'
    result.message='Búsqueda completada; no se garantiza óptimo global.'
    return result
