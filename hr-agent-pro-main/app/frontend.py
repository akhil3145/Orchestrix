"""Premium Streamlit interface for Orchestrix."""

import datetime
import json
from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.backend import get_response
from app.candidate_store import list_candidate_history, save_candidate_analysis
from app.data import employee_names, hr_requests, load_employees
from app.product import (
    admin_insights,
    employee_dashboard,
    knowledge_recommendations,
    recruitment_pipeline,
    route_agent,
    workflow_events,
)
from app.resume_intelligence import (
    analyze_resume,
    candidate_report_markdown,
    extract_text_from_upload,
    ranking_table,
)


st.set_page_config(page_title="Orchestrix", page_icon="O", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
<style>
  :root {
    --surface: rgba(255,255,255,.78);
    --line: rgba(15,23,42,.10);
    --ink: #101828;
    --muted: #667085;
    --brand: #2563eb;
    --ok: #079455;
    --warn: #dc6803;
  }
  .stApp {
    background:
      radial-gradient(circle at 8% 12%, rgba(37,99,235,.14), transparent 26rem),
      radial-gradient(circle at 92% 4%, rgba(20,184,166,.12), transparent 24rem),
      linear-gradient(135deg, #f8fafc 0%, #eef2f7 48%, #f7f9fc 100%);
    color: var(--ink);
  }
  [data-testid="stSidebar"] {
    background: rgba(255,255,255,.72);
    border-right: 1px solid var(--line);
    backdrop-filter: blur(18px);
  }
  .hero {
    border: 1px solid var(--line);
    background: linear-gradient(135deg, rgba(16,24,40,.96), rgba(29,78,216,.86));
    color: white;
    border-radius: 18px;
    padding: 24px;
    box-shadow: 0 20px 50px rgba(15,23,42,.12);
  }
  .hero h1 { font-size: 2rem; line-height: 1.15; margin: 0 0 8px 0; letter-spacing: 0; }
  .hero p { margin: 0; color: rgba(255,255,255,.76); max-width: 760px; }
  .metric-card, .panel {
    border: 1px solid var(--line);
    background: var(--surface);
    border-radius: 14px;
    padding: 18px;
    box-shadow: 0 12px 30px rgba(15,23,42,.06);
    backdrop-filter: blur(14px);
  }
  .metric-label { color: var(--muted); font-size: .78rem; text-transform: uppercase; letter-spacing: .08em; }
  .metric-value { font-size: 1.55rem; font-weight: 750; margin-top: 4px; }
  .tag {
    display: inline-flex; align-items: center; gap: 6px;
    border: 1px solid var(--line); border-radius: 999px;
    padding: 4px 9px; font-size: .78rem; color: #344054; background: rgba(255,255,255,.62);
    margin: 2px 4px 2px 0;
  }
  .timeline {
    border-left: 2px solid rgba(37,99,235,.25);
    padding-left: 14px;
  }
  .timeline-item { margin: 0 0 14px 0; }
  .small-muted { color: var(--muted); font-size: .86rem; }
  .candidate-card {
    border: 1px solid var(--line);
    background: rgba(255,255,255,.76);
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 10px 26px rgba(15,23,42,.06);
  }
  .score-pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 64px;
    height: 34px;
    border-radius: 999px;
    background: rgba(7,148,85,.12);
    color: #067647;
    font-weight: 800;
  }
  div[data-testid="stMetric"] {
    border: 1px solid var(--line);
    background: rgba(255,255,255,.70);
    border-radius: 14px;
    padding: 14px;
  }
  .stTabs [data-baseweb="tab-list"] { gap: 8px; }
  .stTabs [data-baseweb="tab"] {
    border: 1px solid var(--line);
    border-radius: 999px;
    padding: 8px 14px;
    background: rgba(255,255,255,.62);
  }
</style>
""",
    unsafe_allow_html=True,
)


def init_state():
    defaults = {
        "messages": [],
        "current_user": employee_names()[0] if employee_names() else "Guest",
        "model": "claude",
        "kb_query": "",
        "latest_candidate_analysis": None,
        "latest_candidate_report": "",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def card(label: str, value: str, detail: str = ""):
    st.markdown(
        f"""
<div class="metric-card">
  <div class="metric-label">{label}</div>
  <div class="metric-value">{value}</div>
  <div class="small-muted">{detail}</div>
</div>
""",
        unsafe_allow_html=True,
    )


init_state()
df = load_employees()
insights = admin_insights()

with st.sidebar:
    st.markdown("### Orchestrix")
    st.caption("AI-native HR operating system")
    st.divider()
    names = employee_names()
    st.session_state.current_user = st.selectbox("Workspace user", names, index=names.index(st.session_state.current_user) if st.session_state.current_user in names else 0)
    st.session_state.model = st.selectbox("AI runtime", ["claude", "ollama"], index=0)
    st.divider()
    st.markdown("#### Operating Signals")
    st.metric("Employees", insights["total_employees"])
    st.metric("Departments", len(insights["department_counts"]))
    st.metric("Burnout indicator", insights["burnout_indicator"])
    st.divider()
    if st.button("Export session", width="stretch"):
        st.download_button(
            "Download JSON",
            data=json.dumps(st.session_state.messages, indent=2, default=str),
            file_name=f"hr-agent-session-{datetime.datetime.now().strftime('%Y%m%d-%H%M')}.json",
            mime="application/json",
            width="stretch",
        )
    if st.button("Clear chat", width="stretch"):
        st.session_state.messages = []
        st.rerun()


st.markdown(
    """
<div class="hero">
  <h1>Orchestrix</h1>
  <p>An AI-powered HR operating system for employee support, recruiting workflows, onboarding, policy intelligence, and people analytics.</p>
</div>
""",
    unsafe_allow_html=True,
)

st.write("")
c1, c2, c3, c4 = st.columns(4)
with c1:
    card("Headcount", str(insights["total_employees"]), "Live employee system")
with c2:
    card("Monthly Payroll", f"PHP {insights['monthly_payroll_php']:,}", "Preview from HR records")
with c3:
    card("Retention", insights["retention_indicator"], "AI operating signal")
with c4:
    card("Avg Leave", f"{insights['avg_vacation_leave']} VL", f"{insights['avg_sick_leave']} SL average")

tab_chat, tab_employee, tab_recruiting, tab_admin, tab_knowledge, tab_roadmap = st.tabs(
    ["Assistant", "Employee", "Recruiting", "Admin", "Knowledge", "Roadmap"]
)

with tab_chat:
    left, right = st.columns([2, 1])
    with left:
        st.subheader("AI HR Assistant")
        quick_actions = st.columns(4)
        prompts = [
            "How many vacation days do I have?",
            "Who is my supervisor?",
            "Summarize my leave balance.",
            "What is the leave encashment policy?",
        ]
        for col, prompt in zip(quick_actions, prompts):
            if col.button(prompt, width="stretch"):
                st.session_state.pending_prompt = prompt

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == "assistant":
                    st.caption(f"{message.get('agent', 'Employee Support Agent')} | Model: {message.get('model', 'local')}")

        pending = st.session_state.pop("pending_prompt", None)
        user_input = pending or st.chat_input("Ask about leave, policy, payroll, onboarding, or recruiting...")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            agent = route_agent(user_input)
            with st.spinner(f"{agent} is working..."):
                result = get_response(
                    user_input=user_input,
                    user=st.session_state.current_user,
                    model=st.session_state.model,
                    session_id=st.session_state.current_user,
                )
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": result["response"],
                    "model": result.get("model_used", "local"),
                    "agent": agent,
                }
            )
            st.rerun()
    with right:
        st.subheader("Agent Router")
        for key, name in {
            "Policy": "Answers handbook and compliance questions",
            "Recruitment": "Scores resumes and advances hiring work",
            "Payroll": "Explains pay, leave value, and calculations",
            "Onboarding": "Coordinates tasks and manager follow-ups",
            "Analytics": "Surfaces workforce risk and trends",
        }.items():
            st.markdown(f"<span class='tag'>{key}</span> {name}", unsafe_allow_html=True)
        st.divider()
        st.caption("Streaming-ready interface: the backend API is preserved and can be upgraded to token streaming without changing the dashboard contract.")

with tab_employee:
    st.subheader("Employee Operating Dashboard")
    dash = employee_dashboard(st.session_state.current_user)
    profile = dash["profile"]
    p1, p2, p3 = st.columns(3)
    p1.metric("Vacation Leave", dash["leave_balance"]["vacation"])
    p2.metric("Sick Leave", dash["leave_balance"]["sick"])
    p3.metric("VL Encashment", f"PHP {dash['payroll_preview']['vl_encashment_value']:,.0f}")
    st.write("")
    a, b = st.columns([1.2, 1])
    with a:
        st.markdown("#### Profile")
        st.dataframe(pd.DataFrame([profile]), width="stretch", hide_index=True)
        st.markdown("#### HR Requests")
        st.dataframe(pd.DataFrame(hr_requests(profile)), width="stretch", hide_index=True)
    with b:
        st.markdown("#### Onboarding")
        for task in dash["onboarding"]:
            st.checkbox(f"{task['task']} - {task['owner']}", value=task["done"], disabled=True)
        st.markdown("#### Performance Pulse")
        st.info(f"{dash['performance']['pulse']} | {dash['performance']['manager_signal']} | Risk: {dash['performance']['risk']}")

with tab_recruiting:
    st.subheader("Resume Intelligence")
    upload_col, rank_col = st.columns([1.05, 1])

    with upload_col:
        st.markdown("#### Analyze Candidate")
        role = st.selectbox(
            "Target role",
            ["HR Generalist", "Technical Recruiter", "People Operations Lead", "Talent Coordinator"],
            index=0,
        )
        uploaded_resume = st.file_uploader("Upload resume PDF or text file", type=["pdf", "txt", "md"])
        manual_resume = st.text_area("Or paste resume text", height=150, placeholder="Paste resume text when a PDF is not available...")

        if st.button("Run AI resume analysis", type="primary", width="stretch"):
            try:
                source_file = uploaded_resume.name if uploaded_resume else "manual-input.txt"
                if uploaded_resume:
                    resume_text = extract_text_from_upload(uploaded_resume.getvalue(), uploaded_resume.name)
                else:
                    resume_text = manual_resume
                analysis = analyze_resume(resume_text, role=role, source_file=source_file)
                candidate_id = save_candidate_analysis(analysis, resume_text, source_file)
                analysis["candidate_id"] = candidate_id
                st.session_state.latest_candidate_analysis = analysis
                st.session_state.latest_candidate_report = candidate_report_markdown(analysis)
                st.success(f"Candidate saved to history as #{candidate_id}.")
            except Exception as exc:
                st.error(str(exc))

        analysis = st.session_state.latest_candidate_analysis
        if analysis:
            score = analysis["ats_score"]
            st.markdown(
                f"""
<div class="candidate-card">
  <div style="display:flex;align-items:center;justify-content:space-between;gap:12px">
    <div>
      <div class="metric-label">Candidate</div>
      <div style="font-size:1.25rem;font-weight:800">{analysis['candidate_name']}</div>
      <div class="small-muted">{analysis['target_role']} | {analysis['recommendation']}</div>
    </div>
    <div class="score-pill">{score}/100</div>
  </div>
</div>
""",
                unsafe_allow_html=True,
            )
            s1, s2, s3, s4 = st.columns(4)
            breakdown = analysis["score_breakdown"]
            s1.metric("Role Match", f"{breakdown['role_match']}/100")
            s2.metric("Experience", f"{breakdown['experience']}/100")
            s3.metric("Keywords", f"{breakdown['keyword_density']}/100")
            s4.metric("Structure", f"{breakdown['resume_structure']}/100")

            st.markdown("#### Candidate Summary")
            st.write(analysis["summary"])
            st.markdown("#### Experience Overview")
            st.write(analysis["experience_overview"])

            st.markdown("#### Detected Skills")
            if analysis["detected_skills"]:
                for skill in analysis["detected_skills"]:
                    st.markdown(
                        f"<span class='tag'>{skill['skill']} | {', '.join(skill['evidence'])}</span>",
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No clear skill signals detected.")

            strengths_col, concerns_col = st.columns(2)
            with strengths_col:
                st.markdown("#### Strengths")
                for item in analysis["strengths"]:
                    st.success(item)
            with concerns_col:
                st.markdown("#### Possible Concerns")
                for item in analysis["possible_concerns"]:
                    st.warning(item)

            st.download_button(
                "Download candidate report",
                data=st.session_state.latest_candidate_report,
                file_name=f"candidate-report-{analysis['candidate_name'].replace(' ', '-').lower()}.md",
                mime="text/markdown",
                width="stretch",
            )

    with rank_col:
        st.markdown("#### Candidate Ranking")
        history = list_candidate_history(limit=25)
        if history:
            ranking = pd.DataFrame(ranking_table(history))
            st.dataframe(ranking, width="stretch", hide_index=True)
            chart = px.bar(ranking.head(10), x="Candidate", y="ATS Score", color="Recommendation", title="Top candidate scores")
            st.plotly_chart(chart, width="stretch")
        else:
            st.info("Upload or paste a resume to build candidate history.")

        st.markdown("#### Workflow")
        st.dataframe(pd.DataFrame(workflow_events()), width="stretch", hide_index=True)

        st.markdown("#### Demo Pipeline")
        pipeline = pd.DataFrame(recruitment_pipeline())
        st.dataframe(pipeline, width="stretch", hide_index=True)

with tab_admin:
    st.subheader("Admin Analytics")
    x1, x2 = st.columns(2)
    with x1:
        dept = pd.DataFrame(insights["department_counts"].items(), columns=["Department", "Employees"])
        st.plotly_chart(px.pie(dept, names="Department", values="Employees", title="Employees by department"), width="stretch")
    with x2:
        st.plotly_chart(px.bar(df, x="name", y=["vacation_leave", "sick_leave"], barmode="group", title="Leave risk view"), width="stretch")
    st.markdown("#### AI Summary")
    st.info(insights["ai_summary"])
    st.markdown("#### Alerts")
    st.dataframe(pd.DataFrame(insights["low_leave_alerts"]), width="stretch", hide_index=True)

with tab_knowledge:
    st.subheader("Knowledge Base")
    st.session_state.kb_query = st.text_input("Search policies", value=st.session_state.kb_query, placeholder="Search leave, probation, encashment...")
    recs = knowledge_recommendations(st.session_state.kb_query)
    for rec in recs:
        st.markdown(
            f"""
<div class="panel">
  <div class="metric-label">{rec['type']} | Signal {rec['signal']}</div>
  <div style="font-weight:700;margin-top:4px">{rec['title']}</div>
</div>
""",
            unsafe_allow_html=True,
        )
        st.write("")

with tab_roadmap:
    st.subheader("Optimization Roadmap")
    st.markdown("#### Implemented in this upgrade")
    st.write("- Modular config, data access, and product-intelligence helpers")
    st.write("- Premium dashboard with Assistant, Employee, Recruiting, Admin, and Knowledge surfaces")
    st.write("- Candidate scoring, agent routing, onboarding tasks, workflow timeline, and admin risk indicators")
    st.write("- Existing backend API and test-facing local answers preserved")
    st.markdown("#### Next production milestones")
    roadmap = [
        ("Database", "Move CSV data to PostgreSQL with Alembic migrations, tenant IDs, and row-level access rules."),
        ("RAG", "Add document ingestion jobs, vector namespaces per workspace, citations, and prompt-injection filters for retrieved text."),
        ("Auth", "Replace demo auth with OIDC, refresh tokens, RBAC policies, audit trails, and organization invitations."),
        ("Realtime", "Split Streamlit prototype into FastAPI plus React for WebSocket token streaming and background workflows."),
        ("DevOps", "Add Sentry, structured JSON logs, CI security scans, Docker image pinning, and Kubernetes manifests."),
    ]
    st.markdown("<div class='timeline'>", unsafe_allow_html=True)
    for title, detail in roadmap:
        st.markdown(f"<div class='timeline-item'><b>{title}</b><br><span class='small-muted'>{detail}</span></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("#### AI workflow engine")
    st.dataframe(pd.DataFrame(workflow_events()), width="stretch", hide_index=True)
