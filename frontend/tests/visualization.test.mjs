import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import ts from 'typescript';

async function loadTS(path){
  const source=await readFile(new URL(path,import.meta.url),'utf8');
  let code=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.ES2022,target:ts.ScriptTarget.ES2022}}).outputText;
  code=code.replaceAll("'three'",JSON.stringify(import.meta.resolve('three')));
  return import('data:text/javascript;base64,'+Buffer.from(code).toString('base64'));
}
const {adaptRun}=await loadTS('../src/adapters/visualization.ts');
const math=await loadTS('../src/utils/sphericalMath3D.ts');
const run=JSON.parse(await readFile(new URL('../../results/base_42.json',import.meta.url),'utf8'));

test('adaptador conserva las 8 posiciones y porcentajes reales de la API',()=>{
  const data=adaptRun(run);
  assert.equal(data.finalState.satellites.length,8);
  for(let i=0;i<8;i++)assert.deepEqual({lat:data.finalState.satellites[i].lat,lon:data.finalState.satellites[i].lon},run.final[i]);
  for(let i=0;i<6;i++)assert.equal(data.finalState.regions[i].coveragePercentage,run.final_evaluation.coverage[i].fraction*100);
});
test('capas respetan activación, objetos, radio y violaciones por satélite',()=>{
  const changed=structuredClone(run);
  changed.scenario.footprint_km=420;
  changed.scenario.zones[0].active=false;
  changed.final_evaluation.violations=['S2: Objeto A'];
  const data=adaptRun(changed);
  assert.equal(data.footprintKm,420);
  assert.equal(data.restrictedZones.length,2);
  assert.equal(data.occupiedObjects.length,2);
  assert.equal(data.finalState.satellites[1].isValid,false);
  assert.equal(data.finalState.satellites[0].isValid,true);
});
test('fallo factible no crea satélites ni datos de demostración',()=>{
  const failed={...run,status:'no_feasible_found',initial:null,final:null,initial_evaluation:null,final_evaluation:null};
  const data=adaptRun(failed);
  assert.equal(data.finalState.satellites.length,0);
  assert.ok(data.finalState.regions.every(r=>r.coveragePercentage===0));
});
test('proyección y casquetes conservan escala y distancia angular incluso en polos',()=>{
  assert.ok(Math.abs(math.latLonToVector3(90,140,5).y-5)<1e-12);
  assert.ok(Math.abs(math.SATELLITE_RADIUS_SCENE/5-(6371+550)/6371)<1e-12);
  for(const lat of [0,90,-90]){
    const center={lat,lon:179};
    const theta=650/6371;
    const normal=math.coordinateToVector3(center,1);
    const border=math.createSphericalBoundary(center,theta,5,96,0);
    for(const p of border){
      assert.ok(Math.abs(p.length()-5)<1e-10);
      assert.ok(Math.abs(Math.acos(Math.min(1,Math.max(-1,p.clone().normalize().dot(normal))))-theta)<1e-10);
    }
    const geometry=math.createSphericalCapGeometry(center,theta,5,8,64,0);
    assert.ok(Array.from(geometry.attributes.position.array).every(Number.isFinite));
    geometry.dispose();
  }
});
