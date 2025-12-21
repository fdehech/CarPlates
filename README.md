# Tunisia Vehicle Plates API (FastAPI)

A clean REST API that scrapes the latest Tunisian vehicle registration plate numbers from **automobile.tn** and exposes them through a structured FastAPI service with Swagger (OpenAPI).

## Features

- FastAPI REST endpoints
- Swagger UI (`/docs`) + ReDoc (`/redoc`)
- Structured output (prefix, series, number, full)
- No caching (every request scrapes upstream)
- Good error handling for upstream/parsing failures

---

## Project Structure

```
CarPlates/
├─ main.py
├─ requirements.txt
└─ README.md
```

---

## Install

### 1) Create & activate a virtual environment (recommended)

**Windows (PowerShell):**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

---

## Run the API

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

Server will be available at:

- API Base: `http://localhost:5000`
- Swagger UI: `http://localhost:5000/docs`
- ReDoc: `http://localhost:5000/redoc`
- OpenAPI JSON: `http://localhost:5000/openapi.json`

---

## Endpoints

### 1) Get all plate categories

**GET** `/api/v1/plates`

Example:
```bash
curl http://localhost:5000/api/v1/plates
```

Response example:
```json
{
  "updated_at": "2025-12-21T15:21:45.011316+00:00",
  "source": "automobile.tn",
  "data": {
    "TUN": {
      "label": "Immatriculation Normale",
      "prefix": "TU",
      "series": 257,
      "number": 6878,
      "full": "TU 257/6878"
    },
    "MC": {
      "label": "Motocyclette",
      "prefix": "MOTO",
      "series": null,
      "number": 123655,
      "full": "MOTO 123655"
    }
  }
}
```

### 2) Get a specific plate type

**GET** `/api/v1/plates/{plate_type}`

Allowed values:
- `TUN`, `RS`, `IT`, `TRAC`, `MC`, `REM`, `AA`, `ES`

Example:
```bash
curl http://localhost:5000/api/v1/plates/TUN
```

Response example:
```json
{
  "type": "TUN",
  "plate": {
    "label": "Immatriculation Normale",
    "prefix": "TU",
    "series": 257,
    "number": 6878,
    "full": "TU 257/6878"
  },
  "updated_at": "2025-12-21T15:21:45.011316+00:00",
  "source": "automobile.tn"
}
```

---

## Error Handling

### Invalid type
Returns **400**:
```json
{
  "detail": "Invalid plate type. Allowed: TUN, RS, IT, TRAC, MC, REM, AA, ES"
}
```

### Upstream failure
Returns **502**:
```json
{
  "detail": "Upstream source unavailable"
}
```

### Parsing failure (site HTML changed)
Returns **500**:
```json
{
  "detail": "Unexpected page structure"
}
```

---

## Notes (Important)

This API scrapes HTML from automobile.tn. If the site changes CSS classes or layout, parsing can break.
If that happens:
- Update the selectors/classes in `main.py` (`C1`, `C2`)
- Or switch to a more stable parsing strategy (ex: locate items by surrounding text)

---

## License

For educational use. Respect the upstream site's terms of service and robots rules.
