# Verificación de la integración

Rama: codex/integracion-astroshield. Fuentes consultadas y descargadas desde GitHub: origin/ismael (6b4b1cb), origin/owen (9ba0d44), origin/feat/geometria-cobertura (aa9cc9c), origin/mario-visualizacion-3d (0d076ef). master local se conserva en 6b4b1cb. No había ramas adicionales de integrantes 5/6 ni main remota al consultar.

| Verificación ejecutada | Resultado observado |
|---|---|
| pytest, ambas carpetas de pruebas | **88 aprobadas**, cero fallidas; una advertencia StarletteDeprecationWarning |
| npm test | **4 aprobadas**, cero fallidas |
| TypeScript + Vite build | **Aprobado**, 2783 módulos; advertencia de bundle >500 kB |
| pip check | No broken requirements found |
| npm ls --all | Lista de problemas vacía |
| OpenAPI guardado frente a app.openapi() | Coinciden; comprobado por prueba automatizada |
| Auditoría de evidencias originales | **21 ejecuciones correctas** |
| Batería integrada completa | **21 ejecuciones nuevas completadas** |
| Auditoría de evidencias integradas | **21 correctas**, fitness/cobertura recalculados y elitismo conservado |
| Comparación original/integrada normalizando con Run | **21 de 21 idénticas**, incluidos parámetros, coordenadas, evaluaciones e historial |
| git diff --check | Sin errores de espacios ni marcadores de conflicto |

Entorno comprobado: Windows, Python 3.12.10 y Node 24.20.0; versiones de paquetes fijadas en requirements-lock.txt y frontend/package-lock.json. No se instaló React 19 ni la aplicación archivada de Mario. Se usó React 18.3.1, Fiber 8.18.0 y Drei 9.122.0 compatibles con el dashboard existente.

## Resultados integrados reales

- Base semilla 42: **0 → 100**, seis regiones suficientemente cubiertas, ocho satélites y cero violaciones.
- Base cinco semillas: media **98.461538**, desviación poblacional **3.076923**.
- Sin mutación: media **95.336538**; diferencia de medias observada **3.125** puntos.
- Espacio reducido experimental: media **48.009615**, desviación **1.789753**, tres regiones suficientes en promedio. Este escenario experimental bloquea los tres primeros objetivos y es diferente del preset reducido de Owen, que se conserva como otro escenario explícito.
- Prioridad nueva en semilla 42: solución anterior bajo nuevos pesos **30.875**, búsqueda nueva **52.958333**.
- Exclusión global de 180°: no_feasible_found con diagnóstico geométrico, sin configuración final falsa.

Datos completos: results/integration/*.json, summary.csv, statistics.json, interpretations.json y cuatro figuras PNG. Las evidencias originales de results/ y docs/04_analisis_resultados.md no se sobrescribieron. Análisis nuevo: docs/10_analisis_integracion.md.

## Verificación manual del flujo integrado

Se iniciaron Uvicorn y Vite locales y se abrió la aplicación. «Evolucionar constelación» ejecutó el motor real. La vista principal mostró fitness 100, seis regiones, ocho satélites y cero violaciones. «Visor 3D» mostró la escena de Mario alimentada por el adaptador de Run, y «Comparar» mostró 8 + 8 marcadores correspondientes a los dos estados de los mismos ocho satélites y 0 → 6 regiones suficientes.

Se probaron arrastre y rueda sobre el Canvas. Se revisó y corrigió el encuadre en una ventana estrecha. El catálogo de Configuración cargó el escenario global de Owen; «Validar solución anterior» mostró las ocho violaciones y fitness 0. Al ejecutar ese escenario se mostró su imposibilidad y no se generaron satélites. Captura real del visor: results/integration-visualizer.png.

## Historial y límites

Merges de integración: d2bd45a (Owen), eb9c6b9 (geometría), 1c61c83 (Mario). Los ajustes funcionales posteriores se registran en un commit adicional de integración. Se conservan los autores de todos los commits fuente; no se fabricaron aportaciones de integrantes. No se realizó push, publicación ni modificación de master/main. Los servidores temporales de QA se detuvieron al finalizar.

La advertencia de Starlette indica deprecación futura de su transporte httpx, no fallos actuales. El bundle (~1.46 MB sin comprimir, ~404 kB gzip) requiere optimización si se amplía el producto. La API conserva sólo 20 ejecuciones en memoria y no simula física orbital. La accesibilidad y el comportamiento en los equipos reales del grupo requieren revisión humana. Las dos implementaciones de cobertura conservan muestreos predeterminados distintos por diseño documentado; la prueba de compatibilidad les proporciona exactamente las mismas muestras.
