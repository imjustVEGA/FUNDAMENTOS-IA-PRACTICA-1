# Registro de verificación de la entrega

El directorio estaba vacío. Se escribió primero docs/01_definicion_problema.md; después se implementaron módulos, pruebas, motor, REST, contratos TypeScript y visualización.

## Comandos ejecutados y resultados

- `python -m venv .venv`: creó el entorno, pero ensurepip falló. Se recuperó instalando desde el pip del Python anfitrión: `python -m pip --python .venv/Scripts/python.exe install -r requirements.txt`.
- `npm.cmd install` en frontend: dependencias instaladas y package-lock.json guardado.
- `python -m pip --python .venv/Scripts/python.exe freeze`: versiones verificadas en requirements-lock.txt.
- `.venv/Scripts/python -m pytest -q --junitxml=results/tests.xml`: **14 aprobadas**, una advertencia de deprecación de Starlette para httpx. Se ejecutó fuera del aislamiento porque asyncio de Windows quedaba bloqueado al abrir su socket interno dentro del sandbox. Los procesos bloqueados se cerraron; no se contabilizaron como pruebas aprobadas.
- `.venv/Scripts/python -m scripts.experiments`: **21 ejecuciones reales completadas**, cuatro gráficos y análisis generado.
- `.venv/Scripts/python -m scripts.verify_evidence`: auditoría de las 21 ejecuciones, incluidos fitness recalculado, generaciones, cobertura, factibilidad, elitismo, inicialización compartida entre tratamientos y mejora de prioridad en semilla 42.
- Exportación de `app.openapi()` y `npm.cmd exec -- openapi-typescript ...`: contratos generados en frontend/openapi.json y src/schema.d.ts.
- `npm.cmd run build`: TypeScript y Vite aprobados. Advertencia de tamaño del paquete por Three.js/Recharts (~1.44 MB sin comprimir); no impide ejecución. Registro en results/frontend-build.txt.
- Uvicorn y Vite iniciados para QA local. GET /api/scenario respondió HTTP 200. Los procesos de preview requirieron salir del aislamiento de red. Las instrucciones estándar del README sirven fuera de este entorno restringido.

## Inspección de navegador realizada

Se ejecutó la optimización desde la UI con parámetros por defecto. Resultado mostrado: fitness 100, seis regiones, ocho satélites, cero violaciones. Se inspeccionó el globo WebGL con contornos de Natural Earth, satélites y huellas. Alternar «Inicial» cambió las métricas a fitness 0 y cero regiones, manteniendo el componente de cámara. La pestaña Resultados mostró la curva real, porcentajes iniciales/finales y las ocho coordenadas. Se cambió el radio de Atlántico Norte a 180° y «Validar solución anterior» marcó la solución INVÁLIDA, listando los ocho satélites excluidos y fitness 0.

Pruebas REST comprueban también escenario, evaluación, validación, optimización, comparación, consulta por ID, historial, configuraciones, JSON inválido y 404.

Captura real guardada en results/interface.png. Los servidores temporales se detuvieron después de comprobarlos; la aplicación se inicia con los comandos del README. El inventario de archivos entregados está en results/file_manifest.txt.

## Revisión humana pendiente

Probar rotación, zoom, dispositivos pequeños, accesibilidad y rendimiento en cada equipo de presentación. Revisar los supuestos científicos y el error de discretización con muestras más densas; confirmar la justificación de pesos con el docente. Cada integrante debe revisar sus módulos y realizar aportaciones Git reales. No se simularon órbitas ni se certificó aptitud para misiones reales.

No se crearon commits ni se atribuyó trabajo individual ficticio. La IA produjo una implementación inicial verificable; el equipo conserva la responsabilidad académica.
