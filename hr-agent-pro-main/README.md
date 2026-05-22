# Orchestrix

Orchestrix is an AI-native HR operating system for employee support, recruiting workflows, onboarding, policy intelligence, resume screening, and people analytics.

It started as an HR assistant, but now presents as a modern SaaS dashboard with dedicated surfaces for chat, employee operations, recruiting, admin insights, knowledge search, and product roadmap planning.

## What It Does

Orchestrix helps HR teams and employees answer routine questions, inspect employee records, analyze resumes, rank candidates, and monitor workforce signals from one clean interface.

Example employee queries:

```text
Employee: How many vacation days do I have left?
Orchestrix: Alexander Verdad has 45 vacation days remaining.

Employee: Who is my supervisor?
Orchestrix: Alexander Verdad's supervisor is Joseph Santos.

Employee: What would my vacation leave be worth if I encash it?
Orchestrix: Based on your basic pay and leave balance, it calculates the encashment value.
```

Example recruiting workflow:

```text
Recruiter uploads a PDF resume
-> Orchestrix extracts text
-> detects skills and experience
-> generates strengths and possible concerns
-> creates an ATS-style score
-> saves the candidate to history
-> ranks candidates by fit
-> exports a markdown candidate report
```

## Product Surfaces

- **Assistant**: AI HR chat with local deterministic answers for common employee questions and model-backed agent responses for richer requests.
- **Employee Dashboard**: leave balances, payroll preview, HR requests, onboarding tasks, and performance pulse.
- **Recruiting Dashboard**: resume upload, PDF/text extraction, AI resume analysis, ATS scoring, candidate ranking, downloadable reports, and saved candidate history.
- **Admin Dashboard**: headcount, department breakdown, leave risk, retention signals, and AI-generated workforce summary.
- **Knowledge Base**: searchable HR policy recommendations and a foundation for semantic policy retrieval.
- **Roadmap**: implementation notes and next production milestones.

## Key Features

### AI HR Assistant

- HR policy, employee data, payroll, onboarding, recruiting, and analytics routing
- Prompt-injection pattern detection
- Rate limiting
- Input sanitization
- Audit logging
- Claude primary model with Ollama local fallback
- Local fast-path answers for common employee questions

### Resume Intelligence

- PDF, text, and markdown resume upload support
- Resume text extraction using `pypdf`
- Candidate summary generation
- Detected skills with evidence terms
- Experience overview
- Strengths and possible concerns
- ATS-style score with breakdowns:
  - role match
  - experience
  - keyword density
  - resume structure
- Candidate ranking table
- Downloadable candidate intelligence reports
- SQLite-backed candidate history in `data/candidates.db`

### HR Analytics

- Workforce headcount
- Department and employment-status breakdowns
- Average vacation and sick leave balances
- Low-leave alerts
- Monthly payroll preview
- Burnout and retention indicators

### Monitoring And Deployment

- FastAPI health server with `/health`, `/ready`, and `/metrics`
- Prometheus-compatible metrics
- Docker and Docker Compose support
- GitHub Actions CI/CD workflow
- Non-root Docker runtime user

## Project Structure

```text
orchestrix/
├── app/
│   ├── auth.py                 # Streamlit auth/RBAC helpers
│   ├── backend.py              # AI agent, local answers, security checks, analytics
│   ├── candidate_store.py      # SQLite candidate history
│   ├── config.py               # Runtime settings
│   ├── data.py                 # Employee data access and dashboard helpers
│   ├── frontend.py             # Streamlit SaaS dashboard
│   ├── health_server.py        # FastAPI health and metrics endpoints
│   ├── product.py              # Product-level dashboard and workflow intelligence
│   └── resume_intelligence.py  # Resume extraction, scoring, reports, ranking helpers
├── tests/
│   ├── test_backend.py
│   ├── test_messaging_system.py
│   ├── test_query_differentiation.py
│   └── test_resume_intelligence.py
├── monitoring/
│   └── prometheus.yml
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── employee_data.csv
├── hr_policy.txt
├── upload_policy.py
├── OPTIMIZATION_ROADMAP.md
├── Dockerfile
├── docker-compose.yml
├── DEPLOYMENT.md
├── requirements.txt
└── .env.template
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| AI Orchestration | LangChain ReAct agent |
| LLM | Anthropic Claude, Ollama fallback |
| Policy Retrieval | Pinecone + HuggingFace embeddings |
| Resume Parsing | pypdf |
| Employee Data | CSV demo dataset |
| Candidate History | SQLite |
| Analytics | pandas + Plotly |
| Health API | FastAPI |
| Metrics | Prometheus client |
| Logging | Loguru |
| Deployment | Docker, Docker Compose, GitHub Actions |

## Setup

### Prerequisites

- Python 3.11+
- Anthropic API key for Claude-backed answers
- Pinecone API key for policy retrieval
- Optional: Ollama for local fallback

### Install

```bash
git clone https://github.com/yourusername/orchestrix.git
cd orchestrix

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

On macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure

Create a `.env` file from `.env.template` and set the relevant values:

```env
ANTHROPIC_API_KEY=sk-ant-your-key
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=tk-policy
DEFAULT_MODEL=claude
ENABLE_SENTIMENT=false
ENABLE_TRANSLATION=true
AUTH_ENABLED=false
CANDIDATE_DB_PATH=data/candidates.db
```

### Upload Policy Documents

Create a Pinecone index named `tk-policy` with:

- dimensions: `384`
- metric: `cosine`
- cloud/region: AWS `us-east-1`

Then run:

```bash
python upload_policy.py
```

### Run Locally

```bash
streamlit run app/frontend.py
```

Open:

```text
http://localhost:8501
```

The app can still answer common employee questions locally even if external AI services are not configured.

## Docker

```bash
docker-compose up -d
```

This starts:

- Orchestrix dashboard on port `8501`
- health and metrics API on port `8001`
- Ollama fallback service
- Prometheus
- Grafana

## Testing

```bash
python -m pytest tests/ -q
```

Current coverage includes:

- input sanitization
- prompt-injection detection
- rate limiting
- local employee answers
- query differentiation
- analytics report generation
- health endpoint structure
- resume intelligence scoring
- candidate report generation
- candidate history persistence

## Environment Variables

| Variable | Required | Description |
|---|---:|---|
| `ANTHROPIC_API_KEY` | Yes for Claude | Anthropic API key |
| `PINECONE_API_KEY` | Yes for policy RAG | Pinecone API key |
| `PINECONE_INDEX_NAME` | Yes for policy RAG | Pinecone index name, default `tk-policy` |
| `PINECONE_ENVIRONMENT` | Yes for policy RAG | Pinecone region, default `us-east-1` |
| `DEFAULT_MODEL` | No | `claude` or `ollama`, default `claude` |
| `ENABLE_SENTIMENT` | No | Enables optional sentiment analysis |
| `ENABLE_TRANSLATION` | No | Enables translation layer |
| `RATE_LIMIT_RPM` | No | Requests per minute per session |
| `AUTH_ENABLED` | No | Enables Streamlit login flow |
| `CANDIDATE_DB_PATH` | No | SQLite database path for candidate history |

## Demo Data

The project ships with sample employee records in `employee_data.csv`.

Sample employees:

| Name | Department | Role | Status |
|---|---|---|---|
| Alexander Verdad | Finance | AR Assistant | Permanent |
| Joseph Pena | Finance | AR Supervisor | Permanent |
| Jinky Francisco | HR | Recruitment Supervisor | Permanent |
| Mark Delos Santos | HR | HR Assistant | Probation |
| Richard Santos | Finance | AR Head | Permanent |

## Production Roadmap

See [OPTIMIZATION_ROADMAP.md](OPTIMIZATION_ROADMAP.md) for the deeper architecture plan.

Near-term production upgrades:

- move employee data from CSV to PostgreSQL
- add Alembic migrations
- replace demo auth with OIDC and refresh-token flow
- add tenant/workspace isolation
- add Redis-backed rate limiting and queues
- move slow AI workflows to Celery or RQ
- add source-cited RAG responses
- add file validation and malware scanning for uploads
- add Sentry, structured JSON logs, dependency scanning, and E2E smoke tests

## License

This project is for demonstration and portfolio use. See [COPYRIGHT](COPYRIGHT).
