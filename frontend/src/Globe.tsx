import {useEffect,useMemo,useState} from 'react';
import {Canvas} from '@react-three/fiber';
import {Html,Line,OrbitControls,Stars} from '@react-three/drei';
import * as THREE from 'three';
import type {Scenario,Point,Evaluation} from './types';

function xyz(lat:number,lon:number,r=1):[number,number,number]{const a=lat*Math.PI/180,b=lon*Math.PI/180;return [r*Math.cos(a)*Math.cos(b),r*Math.sin(a),-r*Math.cos(a)*Math.sin(b)];}
function Cap({point,angle,color}:{point:Point;angle:number;color:string}){
  const {geometry,border}=useMemo(()=>{
    const center=new THREE.Vector3(...xyz(point.lat,point.lon));
    const rotation=new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,1,0),center);
    const vertices:number[]=[]; const border:[number,number,number][]=[];
    const rings=10,segments=80;
    for(let i=0;i<=rings;i++)for(let j=0;j<=segments;j++){
      const t=angle*i/rings,a=2*Math.PI*j/segments;
      const v=new THREE.Vector3(Math.sin(t)*Math.cos(a),Math.cos(t),Math.sin(t)*Math.sin(a)).applyQuaternion(rotation).multiplyScalar(1.008);
      vertices.push(v.x,v.y,v.z);if(i===rings)border.push([v.x,v.y,v.z]);
    }
    const indices:number[]=[];
    for(let i=0;i<rings;i++)for(let j=0;j<segments;j++){const a=i*(segments+1)+j,b=a+segments+1;indices.push(a,b,a+1,b,b+1,a+1);}
    const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));geometry.setIndex(indices);geometry.computeVertexNormals();return {geometry,border};
  },[point.lat,point.lon,angle]);
  useEffect(()=>()=>geometry.dispose(),[geometry]);
  return <group><mesh geometry={geometry}><meshBasicMaterial color={color} transparent opacity={.18} side={THREE.DoubleSide} depthWrite={false}/></mesh><Line points={border} color={color} lineWidth={1.1}/></group>;
}

export default function Globe({scenario,configuration,evaluation,layers}:{scenario:Scenario;configuration:Point[];evaluation:Evaluation|null;layers:Record<string,boolean>}){
  const [coasts,setCoasts]=useState<[number,number,number][][]>([]);
  useEffect(()=>{fetch('/land.geojson').then(r=>r.json()).then(data=>{
    const lines:[number,number,number][][]=[];
    for(const f of data.features){const polygons=f.geometry.type==='Polygon'?[f.geometry.coordinates]:f.geometry.coordinates;for(const poly of polygons)for(const ring of poly)lines.push(ring.map(([lon,lat]:number[])=>xyz(lat,lon,1.003)));}
    setCoasts(lines);
  }).catch(()=>setCoasts([]));},[]);
  const grid=useMemo(()=>{
    const lines:[number,number,number][][]=[];
    for(let a=-60;a<=60;a+=30)lines.push(Array.from({length:181},(_,i)=>xyz(a,i*2-180,1.001)));
    for(let b=-180;b<180;b+=30)lines.push(Array.from({length:91},(_,i)=>xyz(i*2-90,b,1.001)));
    return lines;
  },[]);
  return <Canvas camera={{position:[.4,1.25,3.3],fov:43}} dpr={[1,1.6]} aria-label="Globo terrestre interactivo">
    <ambientLight intensity={1.4}/><directionalLight position={[4,3,5]} intensity={2}/><Stars radius={80} depth={20} count={1600} factor={2} fade/>
    <mesh><sphereGeometry args={[1,80,80]}/><meshPhongMaterial color="#082438" shininess={25}/></mesh>
    <mesh scale={1.025}><sphereGeometry args={[1,64,64]}/><meshBasicMaterial color="#2289c5" transparent opacity={.065} side={THREE.BackSide}/></mesh>
    {grid.map((line,i)=><Line key={'g'+i} points={line} color="#22516a" transparent opacity={.35} lineWidth={.5}/>)}
    {coasts.map((line,i)=><Line key={'c'+i} points={line} color="#4f9aab" lineWidth={.8}/>)}
    {layers.regions&&scenario.regions.map((r,i)=><group key={r.name}><Cap point={r} angle={r.radius_km/6371} color={evaluation?.coverage[i].covered?'#4ce4ab':'#ffbd69'}/><Html position={xyz(r.lat,r.lon,1.035)} center occlude><span className="region-label">{r.name}</span></Html></group>)}
    {layers.zones&&scenario.zones.filter(z=>z.active).map((z,i)=><group key={i}><Cap point={z} angle={z.radius_deg*Math.PI/180} color={z.kind==='object'?'#c19bff':'#ff647f'}/>{layers.labels&&<Html position={xyz(z.lat,z.lon,1.025)} center occlude><span className="zone-label" style={{color:z.kind==='object'?'#c19bff':'#ff9caf'}}>{z.name}</span></Html>}</group>)}
    {configuration.map((p,i)=><group key={i}>
      {layers.footprints&&<Cap point={p} angle={scenario.footprint_km/6371} color="#39d9f3"/>}
      <mesh position={xyz(p.lat,p.lon,1+550/6371)}><octahedronGeometry args={[.017]}/><meshBasicMaterial color="#b8f4ff"/></mesh>
      <Line points={[xyz(p.lat,p.lon,1.012),xyz(p.lat,p.lon,1+550/6371)]} color="#44b4cb" lineWidth={.6}/>
      {layers.labels&&<Html position={xyz(p.lat,p.lon,1.13)} center occlude><span className="sat-label">S{String(i+1).padStart(2,'0')}</span></Html>}
    </group>)}
    <OrbitControls enablePan={false} minDistance={1.5} maxDistance={5} enableDamping dampingFactor={.07}/>
  </Canvas>;
}
