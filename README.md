# AstroShield — Fundamentos de IA

Pruebas del dominio geométrico y de cobertura:

```bash
pytest backend/tests/domain -v
```

## Pruebas

### Backend

cd backend
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/domain -v
