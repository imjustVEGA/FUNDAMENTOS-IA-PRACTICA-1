import {useState} from 'react';
import {Canvas} from '@react-three/fiber';
import {Scene} from './components/globe/Scene';
import {adaptState} from './adapters/visualization';
import type {Scenario,Point,Evaluation} from './types';
import type {VisualizationSelection} from './types/visualization';

/** Vista principal y visor avanzado comparten la escena de Mario. */
export default function Globe({scenario,configuration,evaluation,layers}:{scenario:Scenario;configuration:Point[];evaluation:Evaluation|null;layers:Record<string,boolean>}){
  const [selection,setSelection]=useState<VisualizationSelection|null>(null);
  const state=adaptState(configuration,evaluation,scenario);
  return <><Canvas camera={{position:[-8,4,13],fov:48}} dpr={[1,1.6]} aria-label="Globo terrestre interactivo">
    <Scene initialState={state} finalState={state} view="final" footprintKm={scenario.footprint_km??650} showLabels={layers.labels}
      restrictedZones={scenario.zones.filter(z=>z.active&&z.kind!=='object').map(z=>({...z,angularRadiusDeg:z.radius_deg,type:'restricted'}))}
      occupiedObjects={scenario.zones.filter(z=>z.active&&z.kind==='object').map(z=>({...z,angularRadiusDeg:z.radius_deg,type:'occupied'}))}
      layers={{satellites:true,regions:layers.regions,footprints:layers.footprints,restrictedZones:layers.zones,occupiedObjects:layers.zones,autoRotate:false}}
      onSelect={setSelection}/>
  </Canvas>{selection&&<div className="selection-note" role="status">{selection.kind==='satellite'?selection.data.id:selection.data.name} · {selection.data.lat.toFixed(3)}°, {selection.data.lon.toFixed(3)}° <button onClick={()=>setSelection(null)} aria-label="Cerrar selección">×</button></div>}</>;
}
