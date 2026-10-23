# AstroShield — Evolucionar una constelación inteligente

Aplicación educativa local: ocho satélites, seis regiones y un algoritmo genético explícito. Modelo estático independiente de AstroShield AI/SATCAT/NEO. Empezar por [modelo](docs/01_definicion_problema.md), [algoritmo](docs/02_algoritmo_evolutivo.md) y [resultados reales](docs/04_analisis_resultados.md).

## Instalación

Python 3.11+ y Node 20.19+ o 22.12+. En PowerShell desde la raíz:

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
cd frontend
npm.cmd ci
cd ..
```

Si el Python del equipo no instala pip al crear el entorno, usar `python -m pip --python .venv/Scripts/python.exe install -r requirements.txt` desde una instalación con pip. requirements-lock.txt registra las versiones verificadas de esta entrega en Python 3.12; requirements.txt expresa rangos compatibles.

## Ejecución

Terminal 1, raíz:

```powershell
.venv/Scripts/python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000
```

Terminal 2:

```powershell
cd frontend
npm.cmd run dev
```

Abrir http://127.0.0.1:5173. API documentada: http://127.0.0.1:8000/docs. No se necesitan claves ni servicios externos. El cálculo empieza con «Evolucionar constelación»; los guiones iniciales significan ausencia de ejecución. Las evidencias de experimentos se consultan en su pestaña. No se presentan datos de ejemplo como resultados.

En Configuración se cambian parámetros, pesos, radios y zonas activas. El editor JSON permite cambiar centros, añadir restricciones, radio de observación y número de muestras. «Validar solución anterior» compara la configuración existente con el escenario editado. Las métricas del Run mantienen su escenario original hasta volver a ejecutar. Resultados exporta JSON completo. Las ejecuciones interactivas viven en memoria y la sesión del navegador: exportarlas antes de cerrar. El servidor conserva las últimas 20 para GET por run_id.

## Verificación y evidencias

```powershell
.venv/Scripts/python -m pytest -q
.venv/Scripts/python -m scripts.experiments
cd frontend
npm.cmd run build
```

Los experimentos completos requieren varios minutos. Generan 21 ejecuciones (5 semillas × 4 tratamientos + imposible), CSV, estadísticas, cuatro PNG y docs/04_analisis_resultados.md. La misma semilla y dependencias reproducen el motor; run_id de HTTP es identificador aleatorio ajeno al cálculo. `scripts/verify_evidence.py` audita todos los archivos.

Registro de comprobaciones y advertencias: [docs/08_verificacion_entrega.md](docs/08_verificacion_entrega.md). Captura real del dashboard: [results/interface.png](results/interface.png). Los servidores usados en la verificación se detuvieron al finalizar; usar los dos comandos de ejecución para volver a iniciar.

Para regenerar contratos tras modificar Pydantic:

```powershell
.venv/Scripts/python -c "import json; from backend.api import app; from pathlib import Path; Path('frontend/openapi.json').write_text(json.dumps(app.openapi()),encoding='utf-8')"
cd frontend
npm.cmd exec -- openapi-typescript openapi.json -o src/schema.d.ts
```

## Estructura

| Ruta | Responsabilidad |
|---|---|
| backend/models.py | Contratos y validación |
| backend/geometry.py | Esfera y muestreo |
| backend/coverage.py | Cobertura y fitness |
| backend/constraints.py, scenarios.py | Factibilidad y datos obligatorios |
| backend/evolution.py | Motor genético independiente |
| backend/api.py | REST, comparación y consulta de ejecuciones |
| frontend/src/Globe.tsx | Globo, discos, satélites y cámara |
| frontend/src/App.tsx | Configuración, dashboard y experimentos |
| tests/, scripts/, results/ | Pruebas, ejecuciones y evidencias |
| docs/ | Supuestos, algoritmo, análisis, equipo y uso de IA |

Limitaciones: discretización de 128 muestras, sin dinámica orbital ni separación física obligatoria; no se garantiza óptimo global. Un fallo de búsqueda no prueba imposibilidad salvo casos geométricos directos como la exclusión de 180°. Ver docs/05_arquitectura.md para límites de persistencia y uso local. La revisión humana del equipo y sus commits reales siguen pendientes; véase docs/06_organizacion_equipo.md.

## Integración de geometría y cobertura

El módulo del integrante 2 se conserva en backend/app/domain y sus pruebas en backend/tests/domain. Ejecutar las pruebas de ambos conjuntos desde la raíz con `python -m pytest`. La guía original se conserva en docs/aportes/geometria_README.md; se unificará su contrato con el motor sin eliminar la API académica.
