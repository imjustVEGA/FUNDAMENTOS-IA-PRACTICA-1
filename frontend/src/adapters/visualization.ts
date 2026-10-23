import type {Evaluation,Point,Run,Scenario} from '../types';
import type {OptimizationResponse,OptimizationState} from '../types/visualization';

/** Adaptador único: no calcula fitness ni inventa cobertura en el navegador. */
export function adaptState(configuration:Point[],evaluation:Evaluation|null,scenario:Scenario):OptimizationState {
  return {
    satellites:configuration.map((p,i)=>({...p,id:`S${String(i+1).padStart(2,'0')}`,isValid:!evaluation?.violations.some(v=>v.startsWith(`S${i+1}:`))})),
    regions:scenario.regions.map((r,i)=>({name:r.name,lat:r.lat,lon:r.lon,
      priority:r.weight>=3?'alta':r.weight>=2?'media':'normal',weight:r.weight,radiusKm:r.radius_km??300,
      coveragePercentage:(evaluation?.coverage[i].fraction??0)*100,isCovered:evaluation?.coverage[i].covered??false})),
  };
}

export function adaptRun(run:Run):OptimizationResponse {
  return {
    earthRadiusKm:6371,footprintKm:run.scenario.footprint_km??650,
    initialState:adaptState(run.initial??[],run.initial_evaluation??null,run.scenario),
    finalState:adaptState(run.final??[],run.final_evaluation??null,run.scenario),
    restrictedZones:run.scenario.zones.filter(z=>z.active&&z.kind!=='object').map(z=>({name:z.name,lat:z.lat,lon:z.lon,angularRadiusDeg:z.radius_deg,type:'restricted'})),
    occupiedObjects:run.scenario.zones.filter(z=>z.active&&z.kind==='object').map(z=>({name:z.name,lat:z.lat,lon:z.lon,angularRadiusDeg:z.radius_deg,type:'occupied'})),
  };
}
