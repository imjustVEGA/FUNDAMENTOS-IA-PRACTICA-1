# Copilot instructions

## Build, test, and run

Run Python commands from the project root. The README's commands use PowerShell paths:

```powershell
.venv/Scripts/python -m pytest -q
.venv/Scripts/python -m pytest tests/test_system.py::test_restrictions_boundaries_and_disable -q
.venv/Scripts/python -m scripts.verify_evidence
```

To run the full experiment suite (21 seeded runs; takes several minutes and regenerates evidence and `docs/04_analisis_resultados.md`):

```powershell
.venv/Scripts/python -m scripts.experiments
```

Run the frontend from `frontend/`:

```powershell
npm.cmd ci
npm.cmd run dev
npm.cmd run build
```

`build` runs TypeScript project checks before Vite. There is no configured lint or frontend test script. For local use, run the API from the project root with `.venv/Scripts/python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000` and the frontend dev server from `frontend/`; Vite proxies `/api` and `/evidence` to the API.

## Architecture and contracts

- This is a local educational optimizer, not an orbital simulation. The backend is organized as a pipeline: Pydantic contracts and scenario definitions (`backend/models.py`, `backend/scenarios.py`) feed spherical geometry (`backend/geometry.py`), coverage scoring (`backend/coverage.py`) and exclusion checks (`backend/constraints.py`); `backend/evolution.py` runs the seeded genetic search independently of HTTP. `backend/api.py` exposes evaluation, validation, comparison, optimization, and in-memory run lookup through FastAPI.
- Scenarios are supplied explicitly with requests; do not introduce mutable global scenario state. The API stores only the latest 20 runs in memory. `run_id` identifies an HTTP result and must not affect the optimizer's seeded reproducibility.
- The frontend consumes API `Run` and `Scenario` data. `App.tsx` owns configuration, requests, results, and evidence views; `Globe.tsx` visualizes the supplied points and scenario. Keep the spherical coordinate conversion consistent with the backend: `(cos(lat)cos(lon), sin(lat), -cos(lat)sin(lon))`.
- Pydantic models are the source of truth for API types. After changing them, regenerate `frontend/openapi.json` from `app.openapi()` and `frontend/src/schema.d.ts` with `openapi-typescript` (commands are in `README.md`). `frontend/src/types.ts` should remain aliases of generated schema types rather than duplicate interfaces.

## Repository-specific behavior

- The chromosome is exactly eight latitude/longitude points. `Parameters` and `Scenario` enforce bounds and fixed model dimensions; preserve those validations when changing request or optimizer behavior.
- Coverage is a deterministic, discretized estimate over each region's spherical disk. A region is considered covered at a sample fraction of at least `0.8`; fitness combines weighted fractional coverage with the covered-region threshold score. Feasibility is separate from coverage: an insufficiently covered solution can still be valid, while any active exclusion-zone violation makes it invalid.
- The optimizer uses `numpy.random.default_rng(seed)`, bounded repair attempts, and elitism. Keep seeded runs reproducible and do not describe a failed bounded search as proof of impossibility; only the explicit active 180-degree exclusion is detected as impossible by the model.
- `tests/test_system.py` contains the system tests for geometry edge cases, feasibility, deterministic evolution, serialization, input validation, and API behavior. Use focused pytest node IDs when iterating. The experiment script regenerates tracked evidence, plots, CSV/statistics, and analysis, so avoid running it unless those outputs are intended to change.
- `scripts/experiments.py` is the experiment automation entry point. It currently compares base, no-mutation, reduced-space, priority, and impossible scenarios; the comparable treatments use the same five seeds (`42, 7, 19, 73, 101`). When extending seed sweeps, keep seeds aligned across treatments and compare improvements against the same seed/scenario baseline. It writes per-run JSON, `results/summary.csv`, `results/statistics.json`, four charts, and regenerates `docs/04_analisis_resultados.md`; retain unsuccessful run statuses and distinguish bounded search failures from proven impossibility in the report.
- Results in `results/` are generated evidence, not frontend fixtures. The browser loads evidence from the API's `/evidence` mount; interactive runs are exported as JSON by the UI and are not persisted across API restarts.
