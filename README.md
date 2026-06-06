# 🚀 Orchestrix

<div align="center">

### 🧠 AI-Native HR Operating System

Orchestrix is an intelligent HR platform that combines AI-powered employee assistance, recruiting automation, policy intelligence, onboarding workflows, workforce analytics, and candidate screening into a unified dashboard.

Built to streamline HR operations, Orchestrix helps organizations reduce manual work, improve employee experience, and make smarter hiring decisions through AI-driven insights.

---

### 🌟 Core Capabilities

🤖 AI HR Assistant
📄 Resume Intelligence & ATS Scoring
👥 Employee Operations Dashboard
📊 Workforce Analytics
📚 Policy Knowledge Search (RAG)
🎯 Candidate Ranking & Screening
🔐 Security, Monitoring & Audit Logging
🐳 Docker & Cloud-Ready Deployment

</div>

---

## ✨ Overview

Traditional HR systems are fragmented across multiple tools. Orchestrix brings employee support, recruiting, onboarding, policy search, and analytics into a single AI-native platform.

The system combines deterministic HR workflows with Large Language Models (LLMs) to provide fast, accurate, and context-aware assistance for employees, recruiters, and administrators.

Whether answering employee questions, ranking candidates, analyzing workforce trends, or retrieving HR policies, Orchestrix acts as a centralized intelligence layer for modern HR teams.

---

## 🎯 Key Features

### 🤖 AI HR Assistant

* Natural language HR support
* Employee information lookup
* Payroll and leave assistance
* Onboarding guidance
* Policy recommendations
* Multi-route query handling
* Claude-powered responses with local fallback

### 📄 Resume Intelligence

* PDF resume upload and parsing
* ATS-style candidate scoring
* Skill extraction and evidence detection
* Experience analysis
* Candidate ranking
* Downloadable candidate reports
* Candidate history tracking

### 👥 Employee Operations

* Leave balance tracking
* Payroll previews
* Performance monitoring
* HR request workflows
* Employee onboarding support

### 📊 Workforce Analytics

* Headcount analysis
* Department insights
* Leave utilization tracking
* Retention indicators
* Burnout monitoring
* AI-generated workforce summaries

### 📚 Knowledge Intelligence

* HR policy retrieval
* Semantic search
* Context-aware recommendations
* RAG-powered knowledge assistance

### 🔐 Enterprise Features

* Authentication and RBAC
* Audit logging
* Input sanitization
* Prompt injection detection
* Rate limiting
* Health monitoring
* Metrics collection

---

## 🏗️ System Architecture

```text
┌──────────────────────┐
│    Streamlit UI      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    FastAPI Layer     │
└──────────┬───────────┘
           │
           ▼
┌────────────────────────────────┐
│       AI Orchestration         │
│ Claude • LangChain • Ollama    │
└──────────┬─────────────────────┘
           │
 ┌─────────┴─────────┐
 ▼                   ▼
Knowledge Base   Resume Engine
(Pinecone RAG)   (ATS Scoring)

           ▼
Employee Data • Analytics • SQLite
```

---

## 🛠️ Tech Stack

| Category          | Technologies           |
| ----------------- | ---------------------- |
| Frontend          | Streamlit              |
| Backend           | FastAPI                |
| AI Framework      | LangChain              |
| LLM               | Claude, Ollama         |
| Vector Database   | Pinecone               |
| Resume Processing | pypdf                  |
| Data Analytics    | Pandas, Plotly         |
| Database          | SQLite                 |
| Monitoring        | Prometheus             |
| Deployment        | Docker, GitHub Actions |

---

## 📈 Business Value

✅ Reduces repetitive HR workload

✅ Improves employee self-service experience

✅ Accelerates candidate screening

✅ Centralizes HR knowledge access

✅ Provides actionable workforce insights

✅ Creates a foundation for enterprise HR automation

---

## 🚀 Future Roadmap

* Multi-tenant SaaS architecture
* PostgreSQL migration
* Advanced RAG pipelines
* Candidate-job matching AI
* HR workflow automation
* Slack and Teams integrations
* Enterprise SSO support
* Predictive workforce analytics
