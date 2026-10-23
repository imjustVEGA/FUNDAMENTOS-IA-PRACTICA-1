import { useMemo, useEffect, useState } from 'react';
import { Line, Html, OrbitControls, Stars } from '@react-three/drei';
import type { ThreeEvent } from '@react-three/fiber';
import { useThree } from '@react-three/fiber';
import { DoubleSide, Vector3, PerspectiveCamera } from 'three';
import { EARTH_RADIUS_SCENE, SATELLITE_RADIUS_SCENE, coordinateToVector3, createSphericalBoundary, createSphericalCapGeometry, kilometersToAngularRadius, latLonToVector3 } from '../../utils/sphericalMath3D';
import type { ConfigurationView, CoverageRegion, OptimizationState, RestrictedZone, OccupiedObject, VisualizationLayers, VisualizationSelection, Satellite } from '../../types/visualization';

interface SceneProps {
  initialState: OptimizationState;
  finalState: OptimizationState;
  restrictedZones: RestrictedZone[];
  occupiedObjects: OccupiedObject[];
  view: ConfigurationView;
  layers: VisualizationLayers;
  onSelect: (selection: VisualizationSelection) => void;
  footprintKm?: number;
  showLabels?: boolean;
}

const initialColor = '#66a9ff';
const finalColor = '#66f0df';

export function Scene(props: SceneProps) {
  const { initialState, finalState, restrictedZones, occupiedObjects, view, layers, onSelect, footprintKm=650,showLabels=true } = props;
  const satelliteSets = view === 'initial'
    ? [{ state: initialState, configuration: 'Inicial' as const, color: initialColor }]
    : view === 'final'
      ? [{ state: finalState, configuration: 'Final' as const, color: finalColor }]
      : [
          { state: initialState, configuration: 'Inicial' as const, color: initialColor },
          { state: finalState, configuration: 'Final' as const, color: finalColor },
        ];
  const regions = view === 'initial' ? initialState.regions : finalState.regions;
  const compared = view === 'comparison';
  const {camera,size}=useThree();
  useEffect(()=>{
    if(camera instanceof PerspectiveCamera){
      const vertical=camera.fov*Math.PI/180;
      const horizontal=2*Math.atan(Math.tan(vertical/2)*size.width/size.height);
      const distance=(SATELLITE_RADIUS_SCENE+0.4)/Math.sin(Math.min(vertical,horizontal)/2)*1.1;
      camera.position.setLength(distance);
      camera.updateProjectionMatrix();
    }
  },[camera,size.width,size.height]);

  return <>
    <color attach="background" args={['#050814']} />
    <ambientLight intensity={0.7} />
    <directionalLight position={[7, 4, 8]} intensity={2.2} color="#b7e8ff" />
    <pointLight position={[-7, -2, -6]} intensity={1.8} color="#1761a4" />
    <Stars radius={80} depth={55} count={1800} factor={3.8} saturation={0} fade speed={0.18} />
    <Earth />

    {layers.satellites && satelliteSets.map(({ state, configuration, color }) => state.satellites.map((satellite) => (
      <SatelliteMarker key={`${configuration}-${satellite.id}`} satellite={satellite} configuration={configuration} color={color} showLabel={showLabels&&(view !== 'comparison' || configuration === 'Final')} onSelect={onSelect} />
    )))}
    {layers.footprints && satelliteSets.map(({ state, configuration, color }) => state.satellites.map((satellite) => (
      <SatelliteFootprint key={`footprint-${configuration}-${satellite.id}`} satellite={satellite} color={color} footprintKm={footprintKm} opacity={configuration === 'Inicial' && compared ? 0.045 : compared ? 0.065 : 0.095} />
    )))}
    {layers.regions && regions.map((region) => {
      const initial = initialState.regions.find((item) => item.name === region.name);
      const final = finalState.regions.find((item) => item.name === region.name);
      return <RegionMarker key={region.name} region={region} comparison={compared && initial && final ? { initial: initial.coveragePercentage, final: final.coveragePercentage } : undefined} showLabel={showLabels} onSelect={onSelect} />;
    })}
    {layers.restrictedZones && restrictedZones.map((zone) => <RestrictedMarker key={zone.name} zone={zone} onSelect={onSelect} />)}
    {layers.occupiedObjects && occupiedObjects.map((object) => <OccupiedMarker key={object.name} object={object} onSelect={onSelect} />)}

    <OrbitControls
      makeDefault
      target={[0, 0, 0]}
      enableDamping
      dampingFactor={0.075}
      enablePan
      screenSpacePanning={false}
      minDistance={6.2}
      maxDistance={40}
      minPolarAngle={0.18}
      maxPolarAngle={Math.PI - 0.18}
      autoRotate={layers.autoRotate}
      autoRotateSpeed={0.24}
    />
  </>;
}

function Earth() {
  return <group>
    <mesh>
      <sphereGeometry args={[EARTH_RADIUS_SCENE, 96, 64]} />
      <meshStandardMaterial color="#08172a" roughness={0.88} metalness={0.28} emissive="#061427" emissiveIntensity={0.2} />
    </mesh>
    <mesh>
      <sphereGeometry args={[EARTH_RADIUS_SCENE * 1.009, 64, 48]} />
      <meshBasicMaterial color="#2780ad" wireframe transparent opacity={0.08} depthWrite={false} />
    </mesh>
    <GeographicGrid />
    <NaturalEarthOutlines />
    <mesh>
      <sphereGeometry args={[EARTH_RADIUS_SCENE * 1.055, 64, 64]} />
      <meshBasicMaterial color="#217cb8" transparent opacity={0.035} side={DoubleSide} depthWrite={false} />
    </mesh>
  </group>;
}

function GeographicGrid() {
  const latitudeLines = useMemo(() => Array.from({ length: 11 }, (_, index) => (index - 5) * 15).filter((lat) => lat !== 0), []);
  const longitudeLines = useMemo(() => Array.from({ length: 12 }, (_, index) => index * 30), []);
  return <group>
    {latitudeLines.map((lat) => <Line key={`lat-${lat}`} points={sampleParallel(lat, EARTH_RADIUS_SCENE * 1.012)} color="#43a8ce" transparent opacity={0.18} lineWidth={0.55} />)}
    {longitudeLines.map((lon) => <Line key={`lon-${lon}`} points={sampleMeridian(lon, EARTH_RADIUS_SCENE * 1.012)} color="#43a8ce" transparent opacity={0.14} lineWidth={0.55} />)}
    <Line points={sampleParallel(0, EARTH_RADIUS_SCENE * 1.013)} color="#5ac8e8" transparent opacity={0.32} lineWidth={0.8} />
  </group>;
}

function ContinentOutlines() {
  const outlines: [number, number][][] = [
    [[72, -168], [70, -150], [62, -140], [58, -130], [50, -128], [48, -124], [40, -124], [32, -117], [24, -110], [18, -104], [15, -96], [9, -84], [18, -77], [25, -80], [30, -82], [35, -76], [44, -67], [51, -56], [58, -62], [65, -53], [72, -60], [77, -80], [73, -105], [75, -130], [72, -168]],
    [[12, -80], [8, -76], [2, -78], [-7, -78], [-15, -75], [-23, -70], [-34, -72], [-45, -74], [-55, -68], [-52, -62], [-40, -58], [-30, -50], [-20, -43], [-8, -35], [1, -50], [7, -60], [12, -80]],
    [[36, -10], [44, -9], [50, -5], [56, -7], [59, 3], [55, 10], [60, 20], [69, 28], [70, 40], [61, 44], [55, 37], [50, 30], [45, 16], [40, 10], [36, -10]],
    [[35, -10], [37, 10], [33, 30], [31, 34], [22, 38], [12, 43], [4, 42], [-5, 40], [-12, 43], [-18, 36], [-26, 33], [-34, 26], [-35, 18], [-30, 16], [-22, 14], [-10, 13], [0, 10], [10, 10], [16, 5], [22, -3], [30, -10], [35, -10]],
    [[70, 40], [68, 65], [72, 90], [70, 110], [66, 130], [58, 145], [52, 150], [48, 143], [42, 132], [38, 128], [32, 121], [25, 120], [20, 110], [10, 107], [5, 103], [1, 104], [-6, 115], [-8, 130], [-3, 140], [10, 142], [20, 136], [25, 130], [32, 135], [40, 140], [48, 150], [58, 160], [62, 175], [55, 180], [50, 165], [45, 155], [40, 145], [35, 140], [30, 130], [25, 120], [35, 100], [45, 80], [55, 60], [62, 50], [70, 40]],
    [[-11, 113], [-18, 115], [-25, 114], [-34, 116], [-39, 128], [-35, 138], [-28, 153], [-18, 151], [-12, 140], [-11, 128], [-11, 113]],
  ];

  return <group>{outlines.map((points, index) => <Line key={`continent-${index}`} points={points.map(([lat, lon]) => latLonToVector3(lat, lon, EARTH_RADIUS_SCENE * 1.017))} color="#54bbdb" transparent opacity={0.58} lineWidth={1.15} />)}</group>;
}

function NaturalEarthOutlines() {
  const [outlines,setOutlines]=useState<Vector3[][]|null>(null);
  const [failed,setFailed]=useState(false);
  useEffect(()=>{
    let active=true;
    fetch('/land.geojson').then(r=>{if(!r.ok)throw Error('Geografía no disponible');return r.json();}).then(data=>{
      const lines:Vector3[][]=[];
      for(const feature of data.features){
        const polygons=feature.geometry.type==='Polygon'?[feature.geometry.coordinates]:feature.geometry.coordinates;
        for(const polygon of polygons)for(const ring of polygon)lines.push(ring.map(([lon,lat]:number[])=>latLonToVector3(lat,lon,EARTH_RADIUS_SCENE*1.017)));
      }
      if(active)setOutlines(lines);
    }).catch(()=>{if(active)setFailed(true);});
    return ()=>{active=false;};
  },[]);
  if(failed)return <ContinentOutlines/>;
  return <group>{outlines?.map((points,i)=><Line key={i} points={points} color="#54bbdb" transparent opacity={.58} lineWidth={.8}/>)}</group>;
}

function sampleParallel(lat: number, radius: number): Vector3[] {
  const points: Vector3[] = [];
  for (let lon = -180; lon <= 180; lon += 4) points.push(latLonToVector3(lat, lon, radius));
  return points;
}

function sampleMeridian(lon: number, radius: number): Vector3[] {
  const points: Vector3[] = [];
  for (let lat = -90; lat <= 90; lat += 3) points.push(latLonToVector3(lat, lon, radius));
  return points;
}

function Cap({ center, angularRadius, color, opacity, radius = EARTH_RADIUS_SCENE, offset = 0.02, wireframe = false }: {
  center: { lat: number; lon: number };
  angularRadius: number;
  color: string;
  opacity: number;
  radius?: number;
  offset?: number;
  wireframe?: boolean;
}) {
  const geometry = useMemo(() => createSphericalCapGeometry(center, angularRadius, radius, 10, 64, offset), [center.lat, center.lon, angularRadius, radius, offset]);
  const boundary = useMemo(() => createSphericalBoundary(center, angularRadius, radius, 96, offset + 0.008), [center.lat, center.lon, angularRadius, radius, offset]);
  useEffect(()=>()=>geometry.dispose(),[geometry]);
  return <group>
    <mesh geometry={geometry} renderOrder={3}>
      <meshBasicMaterial color={color} transparent opacity={opacity} side={DoubleSide} depthWrite={false} wireframe={wireframe} />
    </mesh>
    <Line points={boundary} color={color} transparent opacity={Math.min(opacity * 3.8, 0.9)} lineWidth={1} />
  </group>;
}

function SatelliteMarker({ satellite, configuration, color, showLabel, onSelect }: {
  satellite: Satellite;
  configuration: 'Inicial' | 'Final';
  color: string;
  showLabel: boolean;
  onSelect: (selection: VisualizationSelection) => void;
}) {
  const position = useMemo(() => coordinateToVector3(satellite, SATELLITE_RADIUS_SCENE), [satellite.lat, satellite.lon]);
  const subsatellite = useMemo(() => coordinateToVector3(satellite, EARTH_RADIUS_SCENE * 1.006), [satellite.lat, satellite.lon]);
  const selected = () => onSelect({ kind: 'satellite', data: satellite, configuration });
  return <group>
    <Line points={[subsatellite, position]} color={color} transparent opacity={0.54} lineWidth={1} dashed dashSize={0.065} gapSize={0.05} />
    <mesh position={position} onPointerOver={(event: ThreeEvent<PointerEvent>) => { event.stopPropagation(); selected(); }} onClick={(event: ThreeEvent<MouseEvent>) => { event.stopPropagation(); selected(); }}>
      <octahedronGeometry args={[0.078, 1]} />
      <meshStandardMaterial color={satellite.isValid ? color : '#ff5c72'} emissive={satellite.isValid ? color : '#ff243b'} emissiveIntensity={1.6} metalness={0.3} roughness={0.25} />
    </mesh>
    <mesh position={position}>
      <sphereGeometry args={[0.13, 12, 12]} />
      <meshBasicMaterial color={color} transparent opacity={0.09} depthWrite={false} />
    </mesh>
    {showLabel && <Html position={position.clone().multiplyScalar(1.025).toArray()} center distanceFactor={12} zIndexRange={[20, 0]}><span className="globe-label globe-label--satellite">{satellite.id}</span></Html>}
  </group>;
}

function SatelliteFootprint({ satellite, color, opacity,footprintKm }: { satellite: Satellite; color: string; opacity: number;footprintKm:number }) {
  return <Cap center={satellite} angularRadius={kilometersToAngularRadius(footprintKm)} color={color} opacity={opacity} offset={0.015} />;
}

function RegionMarker({ region, comparison, showLabel, onSelect }: {
  region: CoverageRegion;
  comparison?: { initial: number; final: number };
  showLabel: boolean;
  onSelect: (selection: VisualizationSelection) => void;
}) {
  const covered = region.coveragePercentage >= 80;
  const color = covered ? '#31e6ae' : '#ffc15c';
  const position = useMemo(() => coordinateToVector3(region, EARTH_RADIUS_SCENE * 1.035), [region.lat, region.lon]);
  return <group>
    <Cap center={region} angularRadius={kilometersToAngularRadius(region.radiusKm)} color={color} opacity={0.24} offset={0.035} />
    <mesh position={position} onPointerOver={(event: ThreeEvent<PointerEvent>) => { event.stopPropagation(); onSelect({ kind: 'region', data: region, comparison }); }} onClick={(event: ThreeEvent<MouseEvent>) => { event.stopPropagation(); onSelect({ kind: 'region', data: region, comparison }); }}>
      <sphereGeometry args={[0.048, 14, 14]} />
      <meshBasicMaterial color={color} />
    </mesh>
    {showLabel && <Html position={position.clone().multiplyScalar(1.03).toArray()} center distanceFactor={13} zIndexRange={[15, 0]}><span className="globe-label globe-label--region" style={{ color }}>{region.name} · {region.coveragePercentage}%</span></Html>}
  </group>;
}

function RestrictedMarker({ zone, onSelect }: { zone: RestrictedZone; onSelect: (selection: VisualizationSelection) => void }) {
  const position = useMemo(() => coordinateToVector3(zone, EARTH_RADIUS_SCENE * 1.035), [zone.lat, zone.lon]);
  const select = () => onSelect({ kind: 'restricted', data: zone });
  return <group>
    <Cap center={zone} angularRadius={(zone.angularRadiusDeg * Math.PI) / 180} color="#ff485f" opacity={0.23} offset={0.028} />
    <mesh position={position} onPointerOver={(event: ThreeEvent<PointerEvent>) => { event.stopPropagation(); select(); }} onClick={(event: ThreeEvent<MouseEvent>) => { event.stopPropagation(); select(); }}>
      <octahedronGeometry args={[0.065, 0]} /><meshBasicMaterial color="#ff6c78" />
    </mesh>
    <Html position={position.clone().multiplyScalar(1.025).toArray()} center distanceFactor={14} zIndexRange={[10, 0]}><span className="globe-label globe-label--alert">{zone.name}</span></Html>
  </group>;
}

function OccupiedMarker({ object, onSelect }: { object: OccupiedObject; onSelect: (selection: VisualizationSelection) => void }) {
  const position = useMemo(() => coordinateToVector3(object, EARTH_RADIUS_SCENE * 1.04), [object.lat, object.lon]);
  return <group>
    <Cap center={object} angularRadius={(object.angularRadiusDeg * Math.PI) / 180} color="#ff9b53" opacity={0.23} offset={0.032} wireframe />
    <mesh position={position} rotation={[0, 0, Math.PI / 4]} onPointerOver={(event: ThreeEvent<PointerEvent>) => { event.stopPropagation(); onSelect({ kind: 'occupied', data: object }); }} onClick={(event: ThreeEvent<MouseEvent>) => { event.stopPropagation(); onSelect({ kind: 'occupied', data: object }); }}>
      <octahedronGeometry args={[0.072, 0]} /><meshBasicMaterial color="#ff9b53" />
    </mesh>
    <Html position={position.clone().multiplyScalar(1.025).toArray()} center distanceFactor={14} zIndexRange={[10, 0]}><span className="globe-label" style={{ color: '#ffbd82' }}>{object.name}</span></Html>
  </group>;
}
