# AI-SecureCode Architecture

## Overview

The platform is built around a local-first offline workflow. The frontend interacts with the FastAPI backend, which coordinates static scanners, compiler verification, and a local Ollama AI agent.

## Layers

### Frontend

- React + Vite
- Dark cybersecurity dashboard styling
- Access to benchmark, repair, system-health, and analysis pages

### Backend API

- FastAPI service providing REST APIs
- Request validation using Pydantic models
- Security-aware file handling in a sandboxed workspace

### AI Agent Orchestrator

- receives normalized findings
- builds contextual repair prompts
- invokes local Ollama model
- parses structured JSON output
- handles retry loops up to 3 times

### Static Security Layer

- Cppcheck
- Flawfinder
- Semgrep
- Bandit
- ESLint

### Verification Layer

- GCC, G++
- Python syntax checks
- Node syntax checks
- C# compiler checks where available

### Benchmark Layer

- uses real DevGPT dataset
- preserves historical benchmark records
- compares current local results against prior historical values

## Execution Pipeline

1. load benchmark case or user source
2. normalize and classify findings
3. generate local explanation and repair
4. apply repair to temporary workspace copy
5. verify with compiler and re-scan
6. mark final status only when evidence supports the claim

## Design Principles

- no cloud AI dependency
- no API keys required
- no fabricated findings
- no destructive edits to original source
- offline-first operation
