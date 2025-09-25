# Dev Twin FastAPI + ngrok

## Setup

1. Create venv (already created at `venv/`) and upgrade pip:
```bash
python3 -m venv venv
./venv/bin/python -m pip install --upgrade pip
```

2. Install dependencies:
```bash
make install
```

3. Configure ngrok (optional but recommended):
- Copy `.env.example` to `.env`
- Set `NGROK_AUTHTOKEN` to your token
- Optionally set `NGROK_REGION`

4. Run dev server with ngrok tunnel:
```bash
make dev
```
If `NGROK_AUTHTOKEN` is unset, the server still runs locally at `http://127.0.0.1:8000` without a tunnel.

5. Plain run without ngrok helper:
```bash
make run
```

## Endpoints
- `GET /` → `{"status":"ok"}`
- `GET /health` → `{"health":"ok"}`
