# Arquitectura y contratos

Monorepositorio local: Python 3.12+ / FastAPI / NumPy / Pydantic y React 18 / TypeScript / Vite / React Three Fiber / Drei / Three.js / Recharts / Tailwind / Lucide. No servicios remotos en ejecución. Las dependencias se descargan durante instalación. Natural Earth 110m aporta contornos públicos guardados en frontend/public/land.geojson (dominio público, https://www.naturalearthdata.com/about/terms-of-use/). La fuente descargada es https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_land.geojson.

Flujo: controles → OptimizeRequest → FastAPI → evolution → coverage + constraints → geometry. Run devuelve parámetros, escenario, estado, referencia, solución final, evaluaciones y generaciones. El globo lee directamente Point[] y Scenario del Run; no inventa satélites ni órbitas. La transformación visual es (cosφ cosλ, sinφ, −cosφ sinλ). Huellas y exclusiones son casquetes esféricos; los segmentos verticales sólo unen el satélite ilustrativo a su punto subsatelital. Rotación y zoom persisten al alternar inicial/final porque no se remonta Canvas.

Pydantic es la fuente del contrato: frontend/openapi.json y frontend/src/schema.d.ts se generan desde app.openapi() y openapi-typescript. types.ts exporta alias sin duplicar el modelo. Las muestras se generan en backend y la cobertura reportada siempre proviene de la API. El dibujo usa contornos de discos continuos; puede diferir ligeramente del porcentaje discretizado.

Endpoints: GET /api/scenario; POST /api/evaluate, /api/validate, /api/optimize, /api/compare; GET /api/runs/{id}, /history, /configurations. OpenAPI interactivo en /docs. POST compare acepta previous_scenario y scenario y evalúa exactamente los mismos ocho puntos. Los escenarios se envían explícitamente por petición: no existe estado global mutable del escenario. GET scenario entrega el base y la UI mantiene el escenario actual editado.

API síncrona en threadpool; la UI muestra carga y bloquea nuevos lanzamientos mientras espera. No hay progreso en streaming ni cola distribuida. Se conservan las últimas 20 ejecuciones de API en memoria protegida por Lock (se pierden al reiniciar); el botón exporta JSON y los experimentos persisten archivos. Los IDs aleatorios son de transporte y no afectan reproducibilidad del motor. /evidence sirve sólo la carpeta results. Vite proxifica /api y /evidence. Para despliegue público sería necesario autenticación, cuotas y una cola, fuera del alcance local.


## Integración de aportaciones

La arquitectura final y las decisiones de compatibilidad se documentan en [09_integracion_ramas.md](09_integracion_ramas.md). El motor usa fitness del dominio y reparación del paquete restrictions; los dos visores comparten Scene de Mario y un adaptador de Run. GET /api/scenarios y los endpoints detallados /api/restrictions/* complementan el contrato original.
