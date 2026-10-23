"""Auditoría independiente de los JSON guardados."""
from pathlib import Path
import numpy as np
from backend.models import Run
from backend.coverage import Evaluator
import json
import argparse

def main(directory='results'):
    directory=Path(directory)
    count=0
    for file in directory.glob('*_*.json'):
        r=Run.model_validate_json(file.read_text(encoding='utf-8'))
        if r.status=='success':
            assert len(r.final)==8
            e=Evaluator(r.scenario).evaluate([[p.lat,p.lon] for p in r.final])
            assert e.valid and e.model_dump()==r.final_evaluation.model_dump()
            assert all(h.valid_count==r.parameters.population for h in r.history)
            assert all(a.best<=b.best+1e-10 for a,b in zip(r.history,r.history[1:]))
            assert len(r.history)==r.parameters.generations+1
            for h in r.history:
                e=Evaluator(r.scenario).evaluate([[p.lat,p.lon] for p in h.best_configuration])
                assert e.valid and np.isclose(e.fitness,h.best)
        else:
            assert r.final is None and not r.history
        count+=1
    assert count==21, f'Se esperaban 21 ejecuciones, se encontraron {count}'
    stats=json.loads((directory/'statistics.json').read_text(encoding='utf-8'))
    assert stats['priority_comparison']['new']['fitness'] > stats['priority_comparison']['previous_under_new_weights']['fitness']
    assert not stats['restriction_comparison']['previous_under_new_zones']['valid']
    for seed in [42,7,19,73,101]:
        a=Run.model_validate_json((directory/f'base_{seed}.json').read_text(encoding='utf-8'))
        b=Run.model_validate_json((directory/f'no_mutation_{seed}.json').read_text(encoding='utf-8'))
        assert a.initial==b.initial and a.history[0]==b.history[0]
    print(f'{count} ejecuciones auditadas: fitness, cobertura, restricciones, historial y elitismo correctos.')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--directory',default='results')
    main(parser.parse_args().directory)
