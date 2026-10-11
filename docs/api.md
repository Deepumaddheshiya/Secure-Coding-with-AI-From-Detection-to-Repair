# API Reference

The backend exposes REST endpoints for:

- code analysis
- local AI explanation
- secure repair generation
- compiler verification
- benchmark case access
- system health checks
- report generation

## Key Endpoints

- GET /api/health
- POST /api/scan
- POST /api/explain
- POST /api/repair
- POST /api/verify
- POST /api/pipeline/run
- GET /api/benchmark/cases
- GET /api/benchmark/historical
- GET /api/benchmark/case/{case_id}
- POST /api/reports/generate

## Local-Only Constraints

No API key or cloud AI integration is required. All AI operations are performed through local Ollama endpoints and local security tools.
