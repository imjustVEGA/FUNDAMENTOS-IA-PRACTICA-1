# Equipo: responsabilidades propuestas

Esta distribución define propietarios futuros; no atribuye trabajo realizado ni commits a personas. La implementación inicial se preparó con asistencia de IA. Cada integrante debe estudiar, verificar, modificar y registrar aportaciones reales con Git.

| Integrante | Módulos y archivos | Evidencia que debe explicar |
|---|---|---|
| 1 · Ismael | models.py, evolution.py, arquitectura, docs 01/02/05 | Cromosoma, fitness, selección, cruza, mutación, elitismo, presupuestos y límites |
| 2 | geometry.py, coverage.py | Distancia esférica, polos, antimeridiano, muestreo y unión |
| 3 · Owen | backend/restrictions/, constraints.py, scenarios.py, docs/restricciones_owen.md | Exclusiones, bordes, reparación, fallo acotado, escenarios A-E y reevaluación |
| 4 | Globe.tsx, land.geojson | Correspondencia de coordenadas, casquetes, capas y cámara |
| 5 | tests/, scripts/experiments.py, results/ | Reproducibilidad, variabilidad, ablación y estadísticas |
| 6 | App.tsx, style.css, API, README y guías | Flujo de usuario, errores, exportación, contratos y ejecución |

Interfaces compartidas: Point, Scenario, Parameters, Evaluation, Generation y Run. Cambiar contratos requiere regenerar TypeScript y ejecutar pruebas y build. Acuerden revisiones cruzadas 1↔2, 3↔5, 4↔6. Commits con autor real; no se han fabricado aportaciones del equipo.


## Estado tras integrar las ramas publicadas

Se conservaron commits reales de ismael, feat/geometria-cobertura (autor shinee), owen (autor OWEN2703) y mario-visualizacion-3d (autor finebonsai). La tabla de responsabilidades sigue siendo la guía del equipo; los apartados anteriores sobre una implementación inicial asistida describen la base anterior a estas aportaciones. No había ramas separadas para integrantes 5 y 6 al consultar GitHub. Ver docs/09_integracion_ramas.md para historial y decisiones.
