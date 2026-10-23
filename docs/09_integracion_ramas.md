# Integración de ramas de AstroShield

## Inspección y alcance real

Directorio de trabajo: PRACTICA1-IA. Estado inicial limpio, rama ismael, commit 6b4b1cb. Se consultó GitHub y se descargaron todas sus ramas con git fetch origin; las referencias locales anteriores no contenían tres aportaciones ya publicadas.

| Rama fuente | Commit al inspeccionar | Aportación conservada |
|---|---|---|
| ismael | 6b4b1cb | Motor evolutivo, arquitectura, API, dashboard y evidencias base |
| owen | 9ba0d44 | Restricciones detalladas, reparación, escenarios dinámicos, datos JSON y pruebas |
| feat/geometria-cobertura | aa9cc9c | Geometría esférica, regiones, cobertura, fitness y pruebas de dominio |
| mario-visualizacion-3d | 0d076ef | Escena 3D, proyección, casquetes, fichas, capas y comparación simultánea |

GitHub expuso únicamente estas cuatro ramas. No había ramas separadas de integrantes 5 y 6; no se inventan contribuciones ni se afirma haber integrado trabajo que no está publicado. master era una referencia local idéntica a ismael; no se fusionó otra vez ni se modificó. No existía main local ni remota al inspeccionar.

La rama de destino es **codex/integracion-astroshield**, creada desde ismael. Orden: Owen → geometría → Mario → ajustes y verificación conjunta. Owen descendía de la base; geometría y Mario tenían historiales independientes. Se usaron merges con --allow-unrelated-histories sólo después de comprobar esa situación. Sus commits se conservan como ancestros, con autoría original. No hubo rebase, squash, reset --hard ni push forzado. La integración es local; no se publica ni se modifica el remoto automáticamente.

## Conflictos y decisiones

- **.gitignore:** unión de reglas Python, entornos, pruebas y Node; se conservan las exclusiones útiles de las tres versiones.
- **README y definición del problema:** guía ejecutable de la aplicación unificada más explicación de la API de dominio. Los documentos completos del integrante 2 se guardan en docs/aportes/geometria_README.md y geometria_modelo.md.
- **Dos aplicaciones React:** se conserva un único proyecto ejecutable en frontend. Los componentes, tipos, estilos, utilidades y fixture de Mario se trasladan allí. Su scaffold original se archiva en docs/aportes/mario-scaffold como referencia histórica, no como segundo punto de entrada. Su historial conserva además las rutas originales.
- **React 18 frente a React 19:** se mantiene React 18 + Fiber 8 + Drei 9 del dashboard probado; los componentes de Mario usan APIs compatibles. No se mezclan dos runtimes React ni se instalan los paquetes archivados. TypeScript, build y pruebas verifican la adaptación.
- **Contratos de geometría distintos:** Pydantic Scenario/Point/Run es el contrato externo. El módulo del integrante 2 conserva RegionInteres/CoberturaRegion. El Evaluator usa su agregación fitness_por_cobertura; una prueba contrasta ambos evaluadores con las mismas muestras. La distancia angular vectorial y Haversine se conservan como métodos complementarios con unidades explícitas, no se confunden radianes, grados y kilómetros.
- **Muestras distintas:** la API conserva sus 128 puntos deterministas para mantener la comparación con las evidencias base; la API académica mantiene su muestreo aleatorio sembrado de 1000 puntos por defecto. Ambas usan ahora destinos_geodesicos con una base tangente estable. Las métricas de muestreos diferentes no se presentan como idénticas.
- **Restricciones:** constraints y scenarios reexportan el paquete de Owen. El motor delega la reparación en reparar_configuracion con el mismo generador y presupuesto; no mantiene otra reparación divergente. Se conservan /api/validate y /api/compare y se añaden los informes detallados /api/restrictions/validate y /api/restrictions/compare. GET /api/scenarios alimenta los escenarios preparados en la UI.
- **Visor:** Globe.tsx y GlobeVisualizer usan la misma Scene de Mario. adapters/visualization.ts transforma el Run real, filtra zonas inactivas y transmite radios y porcentajes. Se elimina el mock por defecto; el fixture original se conserva sólo para estudio, sin importarlo en la aplicación. El visor admite inicial/final/comparación, selección, capas, rotación, zoom y autorrotación. Los contornos Natural Earth se conservan; los contornos simplificados de Mario quedan como respaldo si falla la carga local.
- **Reproducibilidad:** los resultados originales no se sobrescriben. La versión integrada genera su conjunto en results/integration y el análisis en docs/10_analisis_integracion.md.

## Correcciones de integración

1. El muestreo original de ambos módulos degeneraba exactamente en ±90°: la fórmula de longitud dividía cantidades casi nulas. Se reemplazó por destino vectorial con base norte/este. Nuevas pruebas comprueban dispersión en ambas direcciones y radio de las muestras en ambos polos.
2. validar_coordenadas podía fallar al describir coordenadas no numéricas. Ahora reporta la infracción sin lanzar TypeError. is_valid_point convierte entradas numéricas antes de comprobar finitud.
3. actualizar_objeto validaba parcialmente después de asignar campos. Ahora valida una copia completa con Zone antes de modificar el objeto; un error no deja un escenario parcialmente alterado.
4. El escenario C decía que 10° de longitud a latitud -30° eran una distancia angular de 10°. Se cambió el punto de borde a una separación meridional exacta de 10°.
5. El visor incluía radios y contadores constantes. Ahora recibe radio de huella, cantidades y pesos reales. El encuadre se ajusta al aspecto de la ventana y se liberan las geometrías al desmontarlas.
6. pytest.ini descubre los dos conjuntos de pruebas y resuelve las importaciones académicas app.domain. backend/requirements.txt remite a la lista raíz. El README especifica Python 3.12+ para el lock verificado de NumPy.

## Verificación

Comandos: `python -m pytest -q`, `npm test`, `npm run build`, `python -m scripts.verify_evidence`, `python -m scripts.experiments --output results/integration --analysis docs/10_analisis_integracion.md` y `python -m scripts.verify_evidence --directory results/integration`.

Las nuevas pruebas contrastan contrato OpenAPI, evaluadores, dispersión polar, catálogo REST, escenarios inviables, atomicidad de edición, datos no numéricos, adaptación de las ocho posiciones y porcentajes, capas, radios y geometría Three.js. Los reportes finales y sus resultados están en results/integration-verification.md.

En navegador se ejecutó semilla 42: fitness 100, 6 regiones, 8 satélites, cero violaciones. El visor comparó 0 → 6 regiones y 8 + 8 marcadores de los dos estados (no 16 satélites distintos). Se probaron arrastre y rueda; el catálogo de Owen permitió revalidar con la exclusión global e identificar las ocho infracciones. Ejecutar ese escenario devolvió el mensaje de imposibilidad sin satélites ficticios. Captura: results/integration-visualizer.png.

## Límites

Persistencia de API en memoria (20 ejecuciones), sin dinámica orbital ni garantía de óptimo global. Advertencias conocidas: cliente httpx de Starlette deprecado y bundle Three.js/Recharts grande. No son fallos de ejecución, pero deben revisarse antes de ampliar el proyecto. La revisión de accesibilidad, dispositivos móviles y supuestos físicos sigue correspondiendo al equipo. No se puede verificar trabajo de integrantes que no está en ninguna rama disponible.
