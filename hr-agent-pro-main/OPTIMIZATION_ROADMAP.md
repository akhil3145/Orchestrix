# Orchestrix Optimization Roadmap

## Audit Summary

The project is a compact Streamlit plus Python AI assistant. It already has useful pieces: local employee-answer fallbacks, LangChain/Pinecone policy retrieval, prompt-injection checks, rate limiting, audit logs, Docker, health probes, Prometheus metrics, and tests.

The main weaknesses were:

- Backend concerns were concentrated in `app/backend.py`, which made configuration, data access, AI orchestration, analytics, and security harder to evolve independently.
- The frontend looked like a chatbot demo rather than an HR operating system. Recruiting, employee operations, knowledge, and admin analytics were not first-class product surfaces.
- Runtime configuration used hardcoded defaults in multiple places, including an outdated `openai` default even though the backend only supports Claude and Ollama.
- Employee data is CSV-based, so it is useful for a portfolio demo but not yet enterprise-grade for permissions, tenancy, auditability, or reporting scale.
- RAG relies on a single Pinecone index with no tenant namespaces, citation model, ingestion status, or retrieved-context security filter.
- Authentication is Streamlit-local demo auth. It needs production OIDC, refresh tokens, RBAC enforcement, and organization-level permissions.
- CI covers tests and Docker build, but does not yet include dependency scanning, image pinning checks, SAST, secret scanning, or E2E smoke tests.

## Implemented Upgrade Slice

- Added `app/config.py` for centralized runtime settings.
- Added `app/data.py` for cached employee data access, profile lookup, HR request data, onboarding tasks, and workforce metrics.
- Added `app/product.py` for product intelligence: agent routing, employee dashboard composition, recruitment pipeline, resume scoring, knowledge recommendations, workflow events, and admin insights.
- Added `app/resume_intelligence.py` for PDF/text resume extraction, skill detection, ATS scoring, strengths/concerns, candidate summaries, ranking-table support, and markdown report generation.
- Added `app/candidate_store.py` for SQLite-backed candidate history with indexed role/score lookups.
- Rebuilt `app/frontend.py` into a premium SaaS dashboard with Assistant, Employee, Recruiting, Admin, Knowledge, and Roadmap tabs.
- Preserved the existing `get_response` backend contract and local deterministic answers used by the test suite.
- Fixed the load-test timing edge case that could divide by zero on very fast local runs.
- Updated UTC timestamp handling to timezone-aware datetimes.

## Target Architecture

```text
Browser
  |
  | React or Streamlit dashboard
  v
FastAPI gateway
  |-- Auth/RBAC middleware
  |-- WebSocket assistant streaming
  |-- REST APIs for employees, recruiting, knowledge, admin analytics
  |
Services
  |-- AI Orchestrator: routes to policy, support, recruiting, payroll, onboarding, analytics agents
  |-- RAG Service: ingestion, chunking, embeddings, retrieval, citations, prompt-injection filters
  |-- Workflow Engine: queue-backed automations and notifications
  |-- HR Data Service: employees, leave, payroll, org structure, activity logs
  |
Data
  |-- PostgreSQL: normalized tenant, user, employee, candidate, request, audit, workflow tables
  |-- Redis: cache, rate limits, short-lived sessions, background job broker
  |-- Vector DB: policy and knowledge chunks partitioned by tenant/workspace
  |
Observability
  |-- Prometheus metrics
  |-- Grafana dashboards
  |-- Sentry errors
  |-- Structured JSON audit logs
```

## Feature Roadmap

1. Database foundation
   - Move CSV employee data to PostgreSQL.
   - Add Alembic migrations, indexes, tenant IDs, row-level permission filters, and seed data.

2. API foundation
   - Split the app into FastAPI routes, services, repositories, models, schemas, and middleware.
   - Add OpenAPI examples, request validation, pagination, and structured error responses.

3. Enterprise auth
   - Add OIDC login, JWT access/refresh tokens, RBAC policies, audit logs, and workspace invitations.
   - Enforce employee self-service versus HR admin permissions at query time.

4. Production RAG
   - Add document ingestion jobs, vector namespaces, source citations, metadata filtering, and retrieval evaluation tests.
   - Add prompt-injection filtering for both user input and retrieved policy chunks.

5. Multi-agent workflows
   - Implement specialized agents for recruitment, policy, employee support, payroll, onboarding, and analytics.
   - Add a workflow state machine for resume upload to screening to interview to offer to onboarding.

6. Recruiting intelligence
   - Current slice includes resume upload, parsing, skill extraction, job-fit scoring, persistent history, candidate ranking, and downloadable reports.
   - Next: add richer resume validation, candidate comparison, interview summary generation, hiring-decision audit trails, and human-review calibration.

7. People analytics
   - Add retention risk, burnout indicators, leave anomalies, workforce trends, sentiment summaries, and department-level dashboards.

8. Deployment hardening
   - Pin Docker image versions, add non-root runtime checks, CI secret scanning, dependency scanning, SAST, and smoke tests.
   - Add Sentry, uptime checks, production logging, and Kubernetes manifests.

## Scalability Roadmap

- Replace in-memory rate limiting with Redis.
- Move slow AI calls and document processing to Celery or RQ workers.
- Add WebSocket streaming for assistant responses.
- Cache policy retrieval results and employee dashboard aggregates.
- Add database indexes for tenant, employee, department, candidate stage, created time, and audit actor.
- Add load tests for assistant latency, concurrent chats, document ingestion, and dashboard analytics.

## Security Roadmap

- Replace demo auth with production identity provider integration.
- Encrypt secrets and validate environment variables at startup.
- Add file upload MIME/type/size scanning and quarantine unsafe documents.
- Remove arbitrary Python REPL access from agent tools before real enterprise deployment.
- Add strict tool permissions per agent and per user role.
- Add audit trails for every policy answer, employee data access, admin action, and candidate decision.
