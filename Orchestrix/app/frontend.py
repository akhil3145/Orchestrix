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
from app.diagnostics import validate_env
from app.product import (
    admin_insights,
    build_progress,
    employee_dashboard,
    knowledge_recommendations,
    production_backlog,
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

st.set_page_config(page_title="Orchestrix", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
<style>
  :root {
    color-scheme: dark;
    font-family: Inter, system-ui, sans-serif;
    --bg: #060b14;
    --surface: rgba(15, 23, 42, 0.78);
    --surface-soft: rgba(15, 23, 42, 0.55);
    --surface-strong: rgba(15, 23, 42, 0.95);
    --border: rgba(148, 163, 184, 0.18);
    --text: #e2e8f0;
    --muted: #94a3b8;
    --brand: #82aaff;
    --brand-strong: #60a5fa;
    --success: #34d399;
    --warning: #fbbf24;
    --danger: #fb7185;
  }
  .stApp, .css-18e3th9 { background: radial-gradient(circle at top left, rgba(96, 165, 250, 0.12), transparent 28%),
                                    radial-gradient(circle at bottom right, rgba(52, 211, 153, 0.10), transparent 28%),
                                    var(--bg) !important; }
  .block-container { padding-top: 1rem; padding-left: 1rem; padding-right: 1rem; }
  .stSidebar, [data-testid="stSidebar"] { background: rgba(8, 14, 31, 0.92) !important; border-right: 1px solid rgba(148, 163, 184, 0.14); backdrop-filter: blur(18px); }
  .sidebar-brand { padding: 20px 18px 12px; }
  .sidebar-brand h1 { margin: 0; font-size: 1.5rem; letter-spacing: -0.02em; color: white; }
  .sidebar-brand p { margin: 8px 0 0; color: var(--muted); line-height: 1.65; }
  .sidebar-section { padding: 16px 18px 20px; border-radius: 24px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); margin-bottom: 18px; }
  .sidebar-section h2 { margin: 0 0 12px; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.14em; color: var(--muted); }
  .sidebar-metric { display: grid; gap: 4px; margin-bottom: 12px; }
  .sidebar-metric strong { font-size: 1.45rem; color: var(--text); }
  .sidebar-metric span { color: var(--muted); font-size: 0.82rem; }
  .glass-panel { background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(255,255,255,0.08); border-radius: 24px; box-shadow: 0 18px 40px rgba(0, 0, 0, 0.15); backdrop-filter: blur(18px); padding: 24px; margin-bottom: 20px; }
  .glass-panel h2, .glass-panel .stTextInput>div>div>label { margin-top: 0; margin-bottom: 14px; color: #f8fafc; }
  .glass-panel .panel-note { color: var(--muted); font-size: 0.95rem; line-height: 1.7; margin-bottom: 18px; }
  .metric-card { border-radius: 22px; padding: 22px; background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 18px 36px rgba(0,0,0,0.12); color: white; margin-bottom: 16px; }
  .metric-label { color: var(--muted); font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.12em; }
  .metric-value { margin-top: 10px; font-size: 1.75rem; font-weight: 700; }
  .metric-caption { margin-top: 8px; color: var(--muted); font-size: 0.92rem; }
  .panel { border-radius: 24px; padding: 22px; background: rgba(15, 23, 42, 0.72); border: 1px solid rgba(255,255,255,0.08); margin-bottom: 18px; }
  .panel h3 { margin: 0 0 10px; color: white; }
  .panel p { margin: 0; color: var(--muted); }
  .tag { display:inline-flex; align-items:center; gap:8px; border-radius:999px; padding:6px 12px; font-size:0.78rem; background: rgba(96, 165, 250, 0.12); color: #bfdbfe; border:1px solid rgba(96,165,250,0.18); }
  .status-strip { display:grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin-top: 18px; }
  .status-item { padding: 18px; border-radius: 20px; background: rgba(15, 23, 42, 0.78); border: 1px solid rgba(255,255,255,0.08); }
  .status-item b { display:block; font-size:1.1rem; color:white; }
  .status-item span { color: var(--muted); font-size: 0.85rem; }
  .candidate-card { border-radius: 24px; padding: 22px; background: rgba(15, 23, 42, 0.72); border: 1px solid rgba(255,255,255,0.08); margin-bottom: 18px; }
  .candidate-card .score-pill { display:inline-flex; align-items:center; justify-content:center; min-width:72px; height:40px; border-radius:999px; background: rgba(52, 211, 153, 0.14); color: #a7f3d0; font-weight:700; }
  .backlog-card { border-radius: 20px; padding: 18px; background: rgba(15, 23, 42, 0.72); border: 1px solid rgba(255,255,255,0.08); margin-bottom: 14px; }
  .priority { display:inline-flex; border-radius:999px; padding:4px 9px; font-size:.72rem; font-weight:800; background: rgba(96, 165, 250, 0.14); color: #93c5fd; margin-right: 8px; }
  .status-next { color: #34d399; font-weight:800; }
  .status-queued { color: var(--muted); font-weight:800; }
  .small-muted { color: var(--muted); font-size:0.92rem; }
  .streamlit-expanderHeader { color: white !important; }
  .stButton>button { border-radius: 999px !important; }
  .css-14xtw13 { padding-left: 0rem; padding-right: 0rem; }
  .css-1d391kg .st-bb { margin: 0; }
  .stTabs [data-baseweb="tab-list"] { gap: 8px; }
  .stTabs [data-baseweb="tab"] { border: 1px solid rgba(255,255,255,0.08); border-radius: 999px; padding: 10px 18px; background: rgba(255,255,255,0.06); color: white; }
  #MainMenu, .css-1lsmgbg, footer { visibility: hidden; }
  @media (max-width: 900px) {
    .status-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
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
        "page": "Assistant",
        "pending_prompt": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def card(label: str, value: str, detail: str = ""):
    st.markdown(
        f"""
<div class="metric-card">
  <div class="metric-label">{label}</div>
  <div class="metric-value">{value}</div>
  <div class="metric-caption">{detail}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def empty_state(title: str, body: str):
    st.markdown(
        f"""
<div class="panel">
  <h3>{title}</h3>
  <p>{body}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def style_plotly(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0", family="Inter, sans-serif"),
        margin=dict(l=0, r=0, t=32, b=16),
        legend=dict(bgcolor="rgba(255,255,255,0.06)", bordercolor="rgba(255,255,255,0.10)", borderwidth=1),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, color="#cbd5e1")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.12)", zeroline=False, color="#cbd5e1")
    return fig


def render_sidebar(insights, progress):
    st.sidebar.markdown(
        """
<div class="sidebar-brand">
  <h1>Orchestrix</h1>
  <p>AI-native HR platform for employee support, recruiting, onboarding, policy search, and people analytics.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
<div class="sidebar-section">
  <h2>Workspace controls</h2>
</div>
""",
        unsafe_allow_html=True,
    )
    st.sidebar.selectbox("Workspace user", employee_names(), key="current_user", label_visibility="collapsed")
    st.sidebar.selectbox("AI runtime", ["claude", "ollama"], key="model", label_visibility="collapsed")
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
<div class="sidebar-section sidebar-nav">
  <h2>Navigation</h2>
</div>
""",
        unsafe_allow_html=True,
    )
    st.session_state.page = st.sidebar.radio(
        "",
        ["Assistant", "Employee", "Recruiting", "Admin", "Knowledge", "Roadmap"],
        index=["Assistant", "Employee", "Recruiting", "Admin", "Knowledge", "Roadmap"].index(st.session_state.page),
        label_visibility="collapsed",
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"""
<div class="sidebar-section">
  <h2>Signals</h2>
  <div class="sidebar-metric"><strong>{insights['total_employees']}</strong><span>Employees</span></div>
  <div class="sidebar-metric"><strong>{len(insights['department_counts'])}</strong><span>Departments</span></div>
  <div class="sidebar-metric"><strong>{progress['percent']}%</strong><span>Build progress</span></div>
</div>
""",
        unsafe_allow_html=True,
    )
    if st.sidebar.button("Export session"):
        st.sidebar.download_button(
            "Download JSON",
            data=json.dumps(st.session_state.messages, indent=2, default=str),
            file_name=f"hr-agent-session-{datetime.datetime.now().strftime('%Y%m%d-%H%M')}.json",
            mime="application/json",
            key="download_session",
        )
    if st.sidebar.button("Clear chat"):
        st.session_state.messages = []
        st.experimental_rerun()


def render_header(insights, progress):
    st.markdown(
        f"""
<div class="hero-card">
  <h1>Modern HR intelligence for growing teams.</h1>
  <p>Access employee support, recruiting workflows, onboarding checklists, policy search, and people analytics from a polished AI SaaS dashboard.</p>
  <div class="status-strip">
    <div class="status-item"><b>{insights['total_employees']}</b><span>employees indexed</span></div>
    <div class="status-item"><b>{len(list_candidate_history(limit=100))}</b><span>candidate records</span></div>
    <div class="status-item"><b>{progress['percent']}%</b><span>work completed</span></div>
    <div class="status-item"><b>{progress['remaining']}</b><span>items remaining</span></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_overview(insights):
    cols = st.columns(4, gap="large")
    with cols[0]:
        card("Headcount", str(insights['total_employees']), "Active employees")
    with cols[1]:
        card("Monthly payroll", f"PHP {insights['monthly_payroll_php']:,}", "Payroll preview")
    with cols[2]:
        card("Retention", insights['retention_indicator'], "Workforce signal")
    with cols[3]:
        card("Avg leave", f"{insights['avg_vacation_leave']} VL / {insights['avg_sick_leave']} SL", "Average balance")


def render_assistant():
    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.subheader("AI HR Assistant")
    st.markdown("<p class='panel-note'>Ask about leave, payroll, onboarding, policy, or recruiting from one polished AI surface.</p>", unsafe_allow_html=True)
    if not st.session_state.messages:
        empty_state("Welcome to your HR assistant.", "Try one of the quick prompts below or ask a custom question to get started.")
    action_cols = st.columns(4, gap="large")
    quick_actions = [
        "How many vacation days do I have?",
        "Who is my supervisor?",
        "Summarize my leave balance.",
        "What is the leave encashment policy?",
    ]
    for col, prompt in zip(action_cols, quick_actions):
        if col.button(prompt):
            st.session_state.pending_prompt = prompt
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])
            if message['role'] == 'assistant':
                st.caption(f"{message.get('agent', 'Employee Support Agent')} | Model: {message.get('model', 'local')}")
    pending = st.session_state.pop('pending_prompt', None)
    user_input = pending or st.chat_input('Ask about leave, policy, payroll, onboarding, or recruiting...')
    if user_input:
        st.session_state.messages.append({'role': 'user', 'content': user_input})
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
                'role': 'assistant',
                'content': result.get('response', ''),
                'model': result.get('model_used', 'local'),
                'agent': agent,
            }
        )
        # If backend reported an error, surface it to the user as a system message
        if result.get('error'):
            st.session_state.messages.append(
                {
                    'role': 'system',
                    'content': f"⚠️ Backend error: {result.get('error')} (model: {result.get('model_used', 'unknown')})",
                }
            )
        st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_employee():
    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.subheader("Employee Operating Dashboard")
    st.markdown("<p class='panel-note'>A polished employee view for leave balances, onboarding progress, and HR requests.</p>", unsafe_allow_html=True)
    dash = employee_dashboard(st.session_state.current_user)
    cols = st.columns(3, gap="large")
    cols[0].metric("Vacation leave", dash['leave_balance']['vacation'], "Current remaining")
    cols[1].metric("Sick leave", dash['leave_balance']['sick'], "Current remaining")
    cols[2].metric("VL encashment", f"PHP {dash['payroll_preview']['vl_encashment_value']:,.0f}", "Estimated payout")
    left, right = st.columns([1.4, 1], gap="large")
    with left:
        st.markdown("#### Profile")
        st.dataframe(pd.DataFrame([dash['profile']]), width='stretch', hide_index=True)
        st.markdown("#### HR requests")
        st.dataframe(pd.DataFrame(hr_requests(dash['profile'])), width='stretch', hide_index=True)
    with right:
        st.markdown("#### Onboarding tasks")
        for task in dash['onboarding']:
            st.checkbox(task['task'], value=task['done'], disabled=True, help=f"Owner: {task['owner']}")
        st.markdown("#### Performance pulse")
        st.info(f"{dash['performance']['pulse']} — {dash['performance']['manager_signal']} | Risk: {dash['performance']['risk']}")
    st.markdown("</div>", unsafe_allow_html=True)


def render_recruiting():
    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.subheader("Recruiting Intelligence")
    st.markdown("<p class='panel-note'>Upload resumes, score candidates, and review hiring signals from a modern interface.</p>", unsafe_allow_html=True)
    upload_col, ranking_col = st.columns([1.05, 0.95], gap="large")
    with upload_col:
        st.markdown("#### Analyze candidate")
        role = st.selectbox(
            "Target role",
            ["HR Generalist", "Technical Recruiter", "People Operations Lead", "Talent Coordinator"],
            index=0,
        )
        uploaded_resume = st.file_uploader("Upload resume PDF or text file", type=["pdf", "txt", "md"])
        manual_resume = st.text_area("Or paste resume text", height=160, placeholder="Paste resume text when a PDF is not available...")
        if st.button("Run AI resume analysis", type="primary"):
            try:
                source_file = uploaded_resume.name if uploaded_resume else "manual-input.txt"
                if uploaded_resume:
                    resume_text = extract_text_from_upload(uploaded_resume.getvalue(), uploaded_resume.name)
                else:
                    resume_text = manual_resume
                analysis = analyze_resume(resume_text, role=role, source_file=source_file)
                candidate_id = save_candidate_analysis(analysis, resume_text, source_file)
                analysis['candidate_id'] = candidate_id
                st.session_state.latest_candidate_analysis = analysis
                st.session_state.latest_candidate_report = candidate_report_markdown(analysis)
                st.success(f"Candidate saved to history as #{candidate_id}.")
            except Exception as exc:
                st.error(str(exc))
        if st.session_state.latest_candidate_analysis:
            analysis = st.session_state.latest_candidate_analysis
            score = analysis['ats_score']
            st.markdown(
                f"""
<div class="candidate-card">
  <div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:14px;">
    <div>
      <div class="metric-label">Candidate</div>
      <div style="font-size:1.35rem;font-weight:800;color:white;">{analysis['candidate_name']}</div>
      <div class="small-muted">{analysis['target_role']} • {analysis['recommendation']}</div>
    </div>
    <div class="score-pill">{score}/100</div>
  </div>
</div>
""",
                unsafe_allow_html=True,
            )
            breakdown_cols = st.columns(4, gap="large")
            breakdown = analysis['score_breakdown']
            breakdown_cols[0].metric("Role match", f"{breakdown['role_match']}/100")
            breakdown_cols[1].metric("Experience", f"{breakdown['experience']}/100")
            breakdown_cols[2].metric("Keywords", f"{breakdown['keyword_density']}/100")
            breakdown_cols[3].metric("Structure", f"{breakdown['resume_structure']}/100")
            st.markdown("#### Summary")
            st.write(analysis['summary'])
            st.markdown("#### Experience overview")
            st.write(analysis['experience_overview'])
            st.markdown("#### Detected skills")
            if analysis['detected_skills']:
                for skill in analysis['detected_skills']:
                    st.markdown(f"<span class='tag'>{skill['skill']} | {', '.join(skill['evidence'])}</span>", unsafe_allow_html=True)
            else:
                st.caption("No clear skill signals detected.")
            strengths_col, concerns_col = st.columns(2, gap="large")
            with strengths_col:
                st.markdown("#### Strengths")
                for item in analysis['strengths']:
                    st.success(item)
            with concerns_col:
                st.markdown("#### Possible concerns")
                for item in analysis['possible_concerns']:
                    st.warning(item)
            st.download_button(
                "Download candidate report",
                data=st.session_state.latest_candidate_report,
                file_name=f"candidate-report-{analysis['candidate_name'].replace(' ', '-').lower()}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        else:
            empty_state("Ready to screen candidates.", "Upload a resume or paste text to generate a candidate score and report.")
    with ranking_col:
        st.markdown("#### Candidate ranking")
        history = list_candidate_history(limit=25)
        if history:
            ranking = pd.DataFrame(ranking_table(history))
            st.dataframe(ranking, width='stretch', hide_index=True)
            chart = px.bar(ranking.head(10), x='Candidate', y='ATS Score', color='Recommendation', title='Top candidate scores')
            style_plotly(chart)
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info('Candidate history is empty. Start by analyzing a resume.')
        st.markdown("#### Workflow")
        st.dataframe(pd.DataFrame(workflow_events()), width='stretch', hide_index=True)
        st.markdown("#### Hiring pipeline")
        st.dataframe(pd.DataFrame(recruitment_pipeline()), width='stretch', hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_admin():
    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.subheader("HR Analytics")
    st.markdown("<p class='panel-note'>Executive analytics and alerts for workforce health, leave risk, and department trends.</p>", unsafe_allow_html=True)
    summary_cols = st.columns(3, gap="large")
    summary_cols[0].metric("Employees", insights['total_employees'])
    summary_cols[1].metric("Departments", len(insights['department_counts']))
    summary_cols[2].metric("Low leave alerts", len(insights['low_leave_alerts']))
    chart_cols = st.columns(2, gap="large")
    dept = pd.DataFrame(insights['department_counts'].items(), columns=['Department', 'Employees'])
    dept_fig = px.pie(dept, names='Department', values='Employees', title='Employee distribution')
    style_plotly(dept_fig)
    chart_cols[0].plotly_chart(dept_fig, use_container_width=True)
    leave_fig = px.bar(df, x='name', y=['vacation_leave', 'sick_leave'], barmode='group', title='Leave risk by employee')
    style_plotly(leave_fig)
    chart_cols[1].plotly_chart(leave_fig, use_container_width=True)
    st.markdown("#### AI summary")
    st.info(insights['ai_summary'])
    st.markdown("#### Alerts")
    st.dataframe(pd.DataFrame(insights['low_leave_alerts']), width='stretch', hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_knowledge():
    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.subheader("Knowledge Base")
    st.markdown("<p class='panel-note'>Search policy guidance and HR knowledge in a refined destination.</p>", unsafe_allow_html=True)
    st.session_state.kb_query = st.text_input('Search policies', value=st.session_state.kb_query, placeholder='Search leave, probation, encashment...')
    recs = knowledge_recommendations(st.session_state.kb_query)
    if not recs:
        empty_state('No results found.', 'Try a broader query like "vacation" or "payroll".')
    else:
        for rec in recs:
            st.markdown(
                f"""
<div class="panel">
  <div class="metric-label">{rec['type']} • Signal {rec['signal']}</div>
  <div style="font-weight:700;margin-top:10px;color:white;">{rec['title']}</div>
  <div class="small-muted" style="margin-top:10px;">{rec.get('summary', '')}</div>
</div>
""",
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)


def render_roadmap():
    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.subheader("Roadmap")
    st.markdown("<p class='panel-note'>A production-ready backlog for the next stage of Orchestrix.</p>", unsafe_allow_html=True)
    done_cols = st.columns(4, gap="large")
    shipped = [
        ("Dashboard", "SaaS-style operating surface"),
        ("Resume AI", "Upload, score, rank, report"),
        ("Modularity", "Config, data, product services"),
        ("Tests", "26 passing checks"),
    ]
    for col, item in zip(done_cols, shipped):
        with col:
            card(item[0], "Done", item[1])
    st.markdown("#### What is left")
    backlog = production_backlog()
    for item in backlog:
        status_class = 'status-next' if item['status'] == 'Next' else 'status-queued'
        st.markdown(
            f"""
<div class="backlog-card">
  <div><span class="priority">{item['priority']}</span><span class="{status_class}">{item['status']}</span></div>
  <div style="font-size:1.05rem;font-weight:800;margin-top:8px;color:white;">{item['area']}</div>
  <div class="small-muted" style="margin-top:8px;">{item['summary']}</div>
  <div style="margin-top:12px;color:var(--text);"><b>Next action:</b> {item['next_action']}</div>
</div>
""",
            unsafe_allow_html=True,
        )
    st.markdown("#### AI workflow engine")
    st.dataframe(pd.DataFrame(workflow_events()), width='stretch', hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)


init_state()
df = load_employees()
insights = admin_insights()
progress = build_progress()

# Runtime environment validation — surface helpful warnings in the UI
env_warnings = validate_env()
if env_warnings:
    with st.sidebar:
        st.markdown("**Environment warnings**")
        for w in env_warnings:
            st.warning(w)
# Quick log tail for debugging
with st.sidebar.expander("Debug logs (tail)", expanded=False):
    try:
        import os
        log_path = os.path.join("logs", "app.log")
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8", errors="replace") as fh:
                lines = fh.readlines()[-60:]
            st.text("".join(lines))
        else:
            st.info("No logs/app.log found yet.")
    except Exception as e:
        st.error(f"Could not read logs: {e}")

render_sidebar(insights, progress)
render_header(insights, progress)
render_overview(insights)

if st.session_state.page == 'Assistant':
    render_assistant()
elif st.session_state.page == 'Employee':
    render_employee()
elif st.session_state.page == 'Recruiting':
    render_recruiting()
elif st.session_state.page == 'Admin':
    render_admin()
elif st.session_state.page == 'Knowledge':
    render_knowledge()
else:
    render_roadmap()