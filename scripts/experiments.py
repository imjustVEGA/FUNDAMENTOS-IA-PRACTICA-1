"""Ejecutar desde la raíz: python -m scripts.experiments."""
import csv
import json
import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from backend.scenarios import base_scenario
from backend.models import Parameters, Zone
from backend.evolution import optimize
from backend.coverage import Evaluator

OUT=Path('results')

def main(output=OUT, analysis=Path('docs/04_analisis_resultados.md')):
    OUT=Path(output)
    OUT.mkdir(parents=True,exist_ok=True)
    rows=[]
    runs={}
    scenarios={'base':base_scenario()}
    reduced=base_scenario()
    reduced.name='Espacio reducido'
    reduced.zones += [Zone(name=r.name+' bloqueada',lat=r.lat,lon=r.lon,radius_deg=7) for r in reduced.regions[:3]]
    scenarios['reduced']=reduced
    priority=reduced.model_copy(deep=True)
    priority.name='Prioridad Yucatán'
    priority.regions[0].weight=20
    scenarios['priority']=priority
    impossible=base_scenario()
    impossible.zones.append(Zone(name='Exclusión total',lat=0,lon=0,radius_deg=180))
    scenarios['impossible']=impossible
    for label in ['base','no_mutation','reduced','priority','impossible']:
        for seed in ([42] if label=='impossible' else [42,7,19,73,101]):
            s=scenarios['base' if label=='no_mutation' else label]
            p=Parameters(seed=seed,mutation=0 if label=='no_mutation' else .25)
            r=optimize(s,p)
            key=f'{label}_{seed}'
            runs[key]=r
            (OUT/f'{key}.json').write_text(r.model_dump_json(indent=2),encoding='utf-8')
            e=r.final_evaluation
            rows.append(dict(scenario=label,seed=seed,initial=r.initial_evaluation.fitness if e else None,final=e.fitness if e else None,covered=e.covered_regions if e else 0,status=r.status))
            print(key,rows[-1],flush=True)
    with (OUT/'summary.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    stats={}
    for label in ['base','no_mutation','reduced','priority']:
        values=[r['final'] for r in rows if r['scenario']==label]
        stats[label]={'mean':float(np.mean(values)),'std_population':float(np.std(values)),'min':min(values),'max':max(values),'mean_covered':float(np.mean([r['covered'] for r in rows if r['scenario']==label]))}
    old=runs['reduced_42']
    reevaluated=Evaluator(priority).evaluate([[p.lat,p.lon] for p in old.final])
    stats['priority_comparison']={'previous_under_new_weights':reevaluated.model_dump(),'new':runs['priority_42'].final_evaluation.model_dump()}
    # Nueva restricción: evaluar exactamente la solución previa bajo el escenario reducido.
    base=runs['base_42']
    stats['restriction_comparison']={'before':base.final_evaluation.model_dump(),'previous_under_new_zones':Evaluator(reduced).evaluate([[p.lat,p.lon] for p in base.final]).model_dump(),'new':old.final_evaluation.model_dump()}
    (OUT/'statistics.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
    plt.figure(figsize=(9,4))
    plt.plot([h.best for h in base.history],label='Máximo')
    plt.plot([h.mean for h in base.history],label='Promedio')
    plt.xlabel('Generación'); plt.ylabel('Fitness'); plt.legend(); plt.tight_layout(); plt.savefig(OUT/'evolution.png'); plt.close()
    x=np.arange(6)
    plt.figure(figsize=(10,4))
    for off,e,label in [(-.2,base.initial_evaluation,'Inicial'),(.2,base.final_evaluation,'Final')]:
        plt.bar(x+off,[c.fraction*100 for c in e.coverage],width=.4,label=label)
    plt.xticks(x,[c.name for c in base.final_evaluation.coverage],rotation=15,ha='right'); plt.ylabel('Cobertura (%)'); plt.legend(); plt.tight_layout(); plt.savefig(OUT/'coverage.png'); plt.close()
    plt.figure(figsize=(9,4))
    for label in ['base','no_mutation','reduced','priority']:
        selected=[r for r in rows if r['scenario']==label]
        plt.plot([str(r['seed']) for r in selected],[r['final'] for r in selected],marker='o',label=label)
    plt.xlabel('Semilla'); plt.ylabel('Fitness final'); plt.legend(); plt.tight_layout(); plt.savefig(OUT/'seeds.png'); plt.close()
    comparison=stats['restriction_comparison']
    plt.figure(figsize=(7,4)); plt.bar(['Base','Anterior reevaluada','Reoptimizada'],[comparison[k]['fitness'] for k in ['before','previous_under_new_zones','new']]); plt.ylabel('Fitness (inválida = 0)'); plt.tight_layout(); plt.savefig(OUT/'restrictions.png'); plt.close()
    base_stats=stats['base']; nomut=stats['no_mutation']; red=stats['reduced']; pc=stats['priority_comparison']
    text=f'''# Análisis de ejecuciones reales

Generado por `python -m scripts.experiments`. Parámetros completos, escenarios y 121 generaciones por ejecución están en {OUT.as_posix()}/*.json. Cinco semillas: 42, 7, 19, 73, 101. Desviación estándar poblacional (ddof=0).

Base semilla 42: fitness {base.initial_evaluation.fitness:.6f} → {base.final_evaluation.fitness:.6f}; mejora absoluta {base.final_evaluation.fitness-base.initial_evaluation.fitness:.6f} puntos. Regiones suficientes: {base.final_evaluation.covered_regions}/6. Sin cubrir: {', '.join(c.name for c in base.final_evaluation.coverage if not c.covered) or 'ninguna'}. Violaciones finales: {len(base.final_evaluation.violations)}.

Base, cinco semillas: media {base_stats['mean']:.6f}, desviación {base_stats['std_population']:.6f}, mínimo {base_stats['min']:.6f}, máximo {base_stats['max']:.6f}. Sin mutación: media {nomut['mean']:.6f}, desviación {nomut['std_population']:.6f}. La diferencia observada es {base_stats['mean']-nomut['mean']:.6f} puntos; cinco semillas no bastan para generalizar causalidad. Ambos tratamientos comparten semillas e inicialización. La mutación introduce posiciones que la cruza por sí sola no puede crear.

Espacio reducido: media {red['mean']:.6f}, desviación {red['std_population']:.6f}, cobertura media {red['mean_covered']:.2f}/6. La solución base bajo las nuevas zonas es válida: {comparison['previous_under_new_zones']['valid']}. Reoptimizar alcanza {comparison['new']['fitness']:.6f} en semilla 42. La restricción total retorna no_feasible_found sin soluciones falsas; 180° prueba imposibilidad en este modelo. Otros fallos acotados no la prueban.

Cambio de prioridades sobre el escenario reducido: solución anterior reevaluada {pc['previous_under_new_weights']['fitness']:.6f}; nueva búsqueda {pc['new']['fitness']:.6f}. No se afirma mejora si la ejecución no la produce. Comparar sólo fitness entre pesos diferentes carece de sentido: ambas cifras anteriores usan los pesos nuevos.

Una puntuación 100 prueba el máximo de este fitness discretizado, pero no una constelación orbital óptima. Las regiones pequeñas y ocho huellas grandes facilitan saturación. No se recompensa el área fuera de las regiones, ni existe redundancia temporal, combustible o riesgo dinámico. El desempate por separación mejora dispersión sin sacrificar fitness. Las gráficas provienen de estas ejecuciones y no fueron suavizadas ni modificadas.
'''
    Path(analysis).write_text(text,encoding='utf-8')
    (OUT/'interpretations.json').write_text(json.dumps({'analysis':text},ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',default='results')
    parser.add_argument('--analysis',default='docs/04_analisis_resultados.md')
    args=parser.parse_args()
    main(args.output,args.analysis)
