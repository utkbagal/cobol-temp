# MACIS - Stage 1

## Quick start (Stage 1)
1. Copy `.env.example` -> `.env` and set values.
2. Build & run:
   docker compose up --build
3. Visit:
   - FastAPI: http://localhost:8000/health
   - Streamlit UI: http://localhost:8501

## Stage 1 validation checklist
- [ ] `GET /health` returns status ok
- [ ] Upload a small .txt via UI and see ingest/response
- [ ] `GET /tools/policy/POL123` returns mock policy
- [ ] docker-compose runs core + ui

