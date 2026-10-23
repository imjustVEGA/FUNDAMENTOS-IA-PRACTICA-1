import numpy as np
from .geometry import vectors, disk_samples, R, angular
from .constraints import violations
from .models import Evaluation, Coverage
from .app.domain.regions import RegionInteres
from .app.domain.coverage import CoberturaRegion, fitness_por_cobertura

class Evaluator:
    def __init__(self, scenario):
        self.scenario=scenario
        self.samples=np.array([vectors(disk_samples(r.lat,r.lon,r.radius_km,scenario.samples)) for r in scenario.regions])
        self.weights=np.array([r.weight for r in scenario.regions])
        self.regions=[RegionInteres(r.name,r.lat,r.lon,'normal',peso=r.weight) for r in scenario.regions]

    def evaluate(self, coords):
        v=vectors(coords)
        dots=self.samples @ v.T
        fractions=np.mean(np.max(dots,axis=2)>=np.cos(self.scenario.footprint_km/R)-1e-12,axis=1)
        covered=fractions>=.8
        issues=violations(coords,self.scenario)
        # La agregación de aptitud pertenece al módulo de cobertura del integrante 2.
        fitness=fitness_por_cobertura([CoberturaRegion(r,float(f),bool(c)) for r,f,c in zip(self.regions,fractions,covered)])
        separations=np.degrees(np.arccos(np.clip(v@v.T,-1,1)))[np.tril_indices(8,-1)]
        return Evaluation(valid=not issues,status='invalid' if issues else ('valid' if all(covered) else 'valid_insufficient'),
            fitness=float(fitness) if not issues else 0.,covered_regions=int(sum(covered)),
            coverage=[Coverage(name=r.name,fraction=float(f),covered=bool(c),weight=r.weight) for r,f,c in zip(self.scenario.regions,fractions,covered)],
            violations=issues,separation_deg=float(min(separations)))
