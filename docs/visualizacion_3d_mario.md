# Visualización tridimensional AstroShield

## Ejecutar el visor

```bash
npm install
npm run dev
```

La aplicación abre directamente el visor usando los datos de `src/mocks/mockOptimizationData.ts`. Para generar el bundle y comprobar TypeScript:

```bash
npm run build
```

## Coordenadas geográficas y escala

`src/utils/sphericalMath3D.ts` convierte latitud y longitud a radianes y después aplica:

```text
x = r · cos(lat) · sin(lon)
y = r · sin(lat)
z = r · cos(lat) · cos(lon)
```

El eje Y apunta al norte y el meridiano 0° apunta hacia +Z. El radio físico de la Tierra es 6371 km y se representa con cinco unidades Three.js. Por eso la altitud ilustrativa de 550 km se escala con `5 × (6371 + 550) / 6371`.

Los círculos de cobertura y exclusión son casquetes geodésicos. Para cada punto se calcula el rumbo desde el centro y su distancia angular; cada vértice queda sobre la esfera usando `centro · cos(ángulo) + tangente · sin(ángulo)`. El radio de 650 km o 300 km primero se convierte a radianes dividiéndolo entre 6371 km. Las restricciones y exclusiones ya traen su radio angular en grados y se convierten a radianes antes de generar la malla.

## Conectar la API

Los contratos están en `src/types/visualization.ts`. El adaptador del Integrante 6 puede pasar la respuesta normalizada directamente:

```tsx
<GlobeVisualizer optimization={optimizationResponse} />
```

La respuesta usa `initialState` y `finalState`, con arreglos de `satellites` y `regions`, más `restrictedZones` y `occupiedObjects`. Si el cliente del API ya separa esos campos, también acepta:

```tsx
<GlobeVisualizer
  initialConfiguration={response.initialState}
  finalConfiguration={response.finalState}
  restrictedZones={response.restrictedZones}
  occupiedObjects={response.occupiedObjects}
/>
```

Todas las propiedades de datos son opcionales para facilitar la integración incremental; mientras no se inyecten, el visor usa el mock incluido. La cámara y `OrbitControls` se mantienen montados al alternar entre configuración inicial, final y comparativa, de modo que se conserva el encuadre. Las posiciones recibidas se muestran como marcadores y no generan trayectorias orbitales calculadas.
