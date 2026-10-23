import { useState } from 'react';
import { Canvas } from '@react-three/fiber';
import {
  Activity,
  Check,
  CircleHelp,
  Eye,
  Layers3,
  LocateFixed,
  Orbit,
  Satellite as SatelliteIcon,
  ShieldAlert,
  Sparkles,
  X,
} from 'lucide-react';
import { mockOptimizationData } from '../../mocks/mockOptimizationData';
import type {
  ConfigurationView,
  OptimizationResponse,
  OptimizationState,
  RestrictedZone,
  OccupiedObject,
  VisualizationLayers,
  VisualizationSelection,
} from '../../types/visualization';
import { Scene } from './Scene';

export interface GlobeVisualizerProps {
  /** Respuesta normalizada de optimización; si se omite, carga el mock incluido. */
  optimization?: OptimizationResponse;
  /** También se pueden inyectar ambos estados sin envolverlos en OptimizationResponse. */
  initialConfiguration?: OptimizationState;
  finalConfiguration?: OptimizationState;
  restrictedZones?: RestrictedZone[];
  occupiedObjects?: OccupiedObject[];
  className?: string;
}

const layerItems = [
  { key: 'satellites', label: 'Satélites e identificadores', detail: '8 unidades', icon: SatelliteIcon, color: '#8bdfff' },
  { key: 'footprints', label: 'Huellas de observación', detail: '650 km', icon: Activity, color: '#37d9f4' },
  { key: 'regions', label: 'Regiones de interés', detail: '6 zonas', icon: LocateFixed, color: '#59e4bb' },
  { key: 'restrictedZones', label: 'Zonas restringidas', detail: '3 alertas', icon: ShieldAlert, color: '#ff737b' },
  { key: 'occupiedObjects', label: 'Objetos ocupados', detail: 'A · B', icon: Sparkles, color: '#ffad70' },
] as const;

const modeItems: { id: ConfigurationView; label: string }[] = [
  { id: 'initial', label: 'Inicial' },
  { id: 'final', label: 'Final' },
  { id: 'comparison', label: 'Comparar' },
];

const selectionTitle: Record<VisualizationSelection['kind'], string> = {
  satellite: 'Unidad orbital',
  region: 'Región de interés',
  restricted: 'Zona restringida',
  occupied: 'Objeto en órbita',
};

function SelectionCard({ selection, onClose }: { selection: VisualizationSelection; onClose: () => void }) {
  const { kind, data } = selection;
  const name = kind === 'satellite' ? data.id : data.name;

  return (
    <section className="hud-panel w-full rounded-xl p-4" aria-live="polite">
      <div className="mb-3 flex items-start justify-between gap-4">
        <div>
          <p className="eyebrow text-[9px] font-semibold uppercase text-slate-500">{selectionTitle[kind]}</p>
          <h3 className="mt-1 text-sm font-semibold text-slate-100">{name}</h3>
        </div>
        <button aria-label="Cerrar ficha" onClick={onClose} className="rounded-md p-1 text-slate-500 transition hover:bg-white/5 hover:text-white">
          <X size={14} />
        </button>
      </div>
      <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-[11px]">
        <Detail label="Latitud" value={`${data.lat.toFixed(2)}°`} />
        <Detail label="Longitud" value={`${data.lon.toFixed(2)}°`} />
        {kind === 'satellite' && <>
          <Detail label="Altitud ilustrativa" value="550 km" />
          <Detail label="Validez" value={data.isValid ? 'Válido' : 'Inválido'} tone={data.isValid ? 'green' : 'red'} />
          <Detail label="Vista" value={`Configuración ${selection.configuration}`} />
        </>}
        {kind === 'region' && <>
          <Detail label="Prioridad" value={data.priority[0].toUpperCase() + data.priority.slice(1)} />
          <Detail label="Radio objetivo" value={`${data.radiusKm} km`} />
          <Detail label="Cobertura" value={`${data.coveragePercentage}%`} tone={data.isCovered ? 'green' : 'amber'} />
          <Detail label="Estado" value={data.isCovered ? 'Cubierta' : 'No cubierta'} tone={data.isCovered ? 'green' : 'amber'} />
          {selection.comparison && <Detail label="Inicial → final" value={`${selection.comparison.initial}% → ${selection.comparison.final}%`} />}
        </>}
        {kind === 'restricted' && <>
          <Detail label="Radio angular" value={`${data.angularRadiusDeg}°`} tone="red" />
          <Detail label="Tipo" value="Restricción por desechos" />
        </>}
        {kind === 'occupied' && <>
          <Detail label="Radio de exclusión" value={`${data.angularRadiusDeg}°`} tone="amber" />
          <Detail label="Tipo" value="Objeto existente" />
        </>}
      </div>
    </section>
  );
}

function Detail({ label, value, tone }: { label: string; value: string; tone?: 'green' | 'amber' | 'red' }) {
  const toneClass = tone === 'green' ? 'text-emerald-300' : tone === 'amber' ? 'text-amber-300' : tone === 'red' ? 'text-rose-300' : 'text-slate-200';
  return <div><p className="text-[9px] text-slate-500">{label}</p><p className={`mt-0.5 font-medium ${toneClass}`}>{value}</p></div>;
}

export function GlobeVisualizer({
  optimization = mockOptimizationData,
  initialConfiguration,
  finalConfiguration,
  restrictedZones,
  occupiedObjects,
  className = '',
}: GlobeVisualizerProps) {
  const initialState = initialConfiguration ?? optimization.initialState;
  const finalState = finalConfiguration ?? optimization.finalState;
  const zones = restrictedZones ?? optimization.restrictedZones;
  const objects = occupiedObjects ?? optimization.occupiedObjects;
  const [view, setView] = useState<ConfigurationView>('final');
  const [selection, setSelection] = useState<VisualizationSelection | null>(null);
  const [layers, setLayers] = useState<VisualizationLayers>({
    satellites: true,
    footprints: true,
    regions: true,
    restrictedZones: true,
    occupiedObjects: true,
    autoRotate: false,
  });
  const coveredCount = (view === 'initial' ? initialState : finalState).regions.filter((region) => region.isCovered).length;
  const satelliteCount = (view === 'initial' ? initialState : finalState).satellites.length;

  function toggleLayer(key: keyof VisualizationLayers) {
    setLayers((current) => ({ ...current, [key]: !current[key] }));
  }

  return (
    <main className={`globe-shell relative h-[100svh] min-h-[620px] w-full overflow-hidden text-slate-100 ${className}`}>
      <div className="pointer-events-none absolute inset-0 z-0 opacity-50" style={{ backgroundImage: 'radial-gradient(rgba(64,139,174,.14) 0.7px, transparent 0.7px)', backgroundSize: '32px 32px', maskImage: 'linear-gradient(to bottom, black, transparent 82%)' }} />

      <div className="canvas-shell absolute inset-0 z-0">
        <Canvas camera={{ position: [0, 0, 11.4], fov: 38 }} dpr={[1, 1.7]} gl={{ antialias: true, alpha: false }}>
          <Scene
            initialState={initialState}
            finalState={finalState}
            restrictedZones={zones}
            occupiedObjects={objects}
            view={view}
            layers={layers}
            onSelect={setSelection}
          />
        </Canvas>
      </div>

      <header className="pointer-events-none absolute left-5 top-5 z-10 flex items-start gap-3 sm:left-8 sm:top-7">
        <div className="pointer-events-auto grid size-10 place-items-center rounded-xl border border-cyan-300/20 bg-cyan-300/[0.06] text-cyan-200 shadow-[0_0_30px_rgba(34,211,238,.08)]">
          <Orbit size={19} strokeWidth={1.6} />
        </div>
        <div className="pt-0.5">
          <p className="eyebrow text-[9px] font-semibold uppercase text-cyan-200/80">Centro de monitoreo espacial</p>
          <h1 className="mt-1 text-lg font-semibold tracking-[0.12em] text-white sm:text-xl">ASTRO<span className="font-light text-cyan-200">SHIELD</span></h1>
          <p className="mt-1 text-[10px] tracking-wide text-slate-500">Evolución de constelación inteligente <span className="mx-1 text-slate-700">/</span> Vista 3D</p>
        </div>
      </header>

      <div className="pointer-events-none absolute right-5 top-5 z-10 flex items-center gap-2 sm:right-8 sm:top-7">
        <div className="hud-panel flex items-center gap-2 rounded-lg px-3 py-2 text-[10px] text-emerald-200/90">
          <span className="relative flex size-1.5"><span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-400 opacity-60" /><span className="relative inline-flex size-1.5 rounded-full bg-emerald-300" /></span>
          SISTEMA ACTIVO
        </div>
        <div className="hud-panel hidden items-center gap-2 rounded-lg px-3 py-2 text-[10px] text-slate-400 sm:flex">
          <CircleHelp size={13} className="text-cyan-300" /> Arrastra para orbitar <span className="text-slate-700">·</span> rueda para zoom
        </div>
      </div>

      <aside className="absolute bottom-5 left-4 z-10 flex w-[min(280px,calc(100vw-2rem))] flex-col gap-3 sm:bottom-8 sm:left-8 sm:w-[300px]">
        <section className="hud-panel rounded-xl p-4">
          <div className="mb-3 flex items-center justify-between">
            <div className="flex items-center gap-2"><Layers3 size={14} className="text-cyan-300" /><h2 className="text-[11px] font-semibold tracking-wide text-slate-100">CAPAS DEL VISOR</h2></div>
            <span className="text-[9px] text-slate-600">{Object.values(layers).filter(Boolean).length}/6 activas</span>
          </div>
          <div className="space-y-0.5">
            {layerItems.map(({ key, label, detail, icon: Icon, color }) => {
              const enabled = layers[key];
              return <button key={key} onClick={() => toggleLayer(key)} aria-pressed={enabled} className="group flex w-full items-center gap-2.5 rounded-lg px-2 py-2 text-left transition hover:bg-white/[0.035]">
                <Icon size={14} style={{ color: enabled ? color : '#5b6472' }} strokeWidth={1.7} />
                <span className={`flex-1 text-[10px] ${enabled ? 'text-slate-200' : 'text-slate-500'}`}>{label}</span>
                <span className="mr-1 text-[9px] text-slate-600">{detail}</span>
                <span className={`grid size-3.5 place-items-center rounded border transition ${enabled ? 'border-cyan-300/40 bg-cyan-300/15 text-cyan-200' : 'border-slate-700 text-transparent'}`}>{enabled && <Check size={10} />}</span>
              </button>;
            })}
            <button onClick={() => toggleLayer('autoRotate')} aria-pressed={layers.autoRotate} className="group flex w-full items-center gap-2.5 rounded-lg px-2 py-2 text-left transition hover:bg-white/[0.035]">
              <Orbit size={14} className={layers.autoRotate ? 'text-violet-300' : 'text-slate-500'} strokeWidth={1.7} />
              <span className={`flex-1 text-[10px] ${layers.autoRotate ? 'text-slate-200' : 'text-slate-500'}`}>Autorrotación suave</span>
              <span className={`relative h-[17px] w-[30px] rounded-full transition ${layers.autoRotate ? 'bg-violet-400/40' : 'bg-slate-800'}`}><span className={`absolute top-[3px] size-[11px] rounded-full transition-all ${layers.autoRotate ? 'left-[16px] bg-violet-200' : 'left-[3px] bg-slate-500'}`} /></span>
            </button>
          </div>
        </section>

        {selection && <SelectionCard selection={selection} onClose={() => setSelection(null)} />}
      </aside>

      <aside className="absolute right-4 top-[76px] z-10 w-[min(270px,calc(100vw-2rem))] sm:right-8 sm:top-[88px] sm:w-[280px]">
        <section className="hud-panel rounded-xl p-4">
          <div className="mb-3 flex items-center justify-between">
            <div><p className="eyebrow text-[9px] font-semibold uppercase text-slate-500">Optimización genética</p><h2 className="mt-1 text-xs font-semibold text-slate-100">Configuración de constelación</h2></div>
            <SatelliteIcon size={17} className="text-cyan-300" />
          </div>
          <div className="grid grid-cols-3 rounded-lg border border-white/[0.06] bg-black/20 p-1">
            {modeItems.map(({ id, label }) => <button key={id} onClick={() => { setView(id); setSelection(null); }} aria-pressed={view === id} className={`rounded-md px-1 py-2 text-[10px] transition ${view === id ? 'bg-cyan-300/15 font-medium text-cyan-100 shadow-sm' : 'text-slate-500 hover:text-slate-300'}`}>{label}</button>)}
          </div>
          <div className="mt-4 grid grid-cols-2 gap-2">
            <div className="rounded-lg border border-white/[0.05] bg-black/15 p-2.5"><p className="text-[9px] text-slate-500">SATÉLITES VISIBLES</p><p className="mt-1 text-sm font-semibold tabular-nums text-slate-100">{view === 'comparison' ? `${initialState.satellites.length} + ${finalState.satellites.length}` : satelliteCount}<span className="ml-1 text-[9px] font-normal text-slate-600">unidades</span></p></div>
            <div className="rounded-lg border border-white/[0.05] bg-black/15 p-2.5"><p className="text-[9px] text-slate-500">REGIONES CUBIERTAS</p><p className="mt-1 text-sm font-semibold tabular-nums text-emerald-300">{view === 'comparison' ? `${initialState.regions.filter((r) => r.isCovered).length} → ${finalState.regions.filter((r) => r.isCovered).length}` : coveredCount}<span className="ml-1 text-[9px] font-normal text-slate-600">/ 6</span></p></div>
          </div>
          <p className="mt-3 text-[9px] leading-relaxed text-slate-500">Los marcadores muestran posiciones recibidas. No se interpolan ni representan órbitas calculadas.</p>
        </section>
      </aside>

      <div className="pointer-events-none absolute bottom-5 right-5 z-10 hidden items-center gap-3 text-[9px] text-slate-500 sm:flex sm:bottom-8 sm:right-8">
        <span className="flex items-center gap-1.5"><i className="size-1.5 rounded-full bg-emerald-300" /> Cubierta ≥80%</span>
        <span className="text-slate-700">/</span><span className="flex items-center gap-1.5"><i className="size-1.5 rounded-full bg-amber-300" /> Bajo umbral</span>
        <span className="text-slate-700">/</span><span className="flex items-center gap-1.5"><i className="size-1.5 rounded-full bg-rose-400" /> Restricción</span>
      </div>
      <div className="pointer-events-none absolute bottom-[17px] right-5 z-10 flex items-center gap-1 text-[9px] text-slate-600 sm:hidden"><Eye size={11} /> Vista interactiva</div>
    </main>
  );
}
