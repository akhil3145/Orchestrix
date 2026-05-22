"""Product-level intelligence used by the premium Streamlit experience."""

from __future__ import annotations

import re
from typing import Any, Dict, List

from app.data import get_employee, onboarding_tasks, workforce_metrics


AGENT_CATALOG = {
    "recruitment": "Recruitment Agent",
    "policy": "HR Policy Agent",
    "support": "Employee Support Agent",
    "payroll": "Payroll Assistant Agent",
    "onboarding": "Onboarding Agent",
    "analytics": "Analytics Agent",
}


def route_agent(query: str) -> str:
    q = query.lower()
    if any(k in q for k in ["resume", "candidate", "interview", "hiring", "recruit"]):
        return AGENT_CATALOG["recruitment"]
    if any(k in q for k in ["policy", "handbook", "leave rule", "compliance"]):
        return AGENT_CATALOG["policy"]
    if any(k in q for k in ["salary", "payroll", "encashment", "basic pay"]):
        return AGENT_CATALOG["payroll"]
    if any(k in q for k in ["onboard", "probation", "regularization"]):
        return AGENT_CATALOG["onboarding"]
    if any(k in q for k in ["analytics", "headcount", "burnout", "retention"]):
        return AGENT_CATALOG["analytics"]
    return AGENT_CATALOG["support"]


def employee_dashboard(name: str) -> Dict[str, Any]:
    employee = get_employee(name)
    if not employee:
        return {}
    vacation = float(employee.get("vacation_leave", 0))
    sick = float(employee.get("sick_leave", 0))
    salary = int(employee.get("basic_pay_in_php", 0))
    return {
        "profile": employee,
        "leave_balance": {"vacation": vacation, "sick": sick, "total": vacation + sick},
        "payroll_preview": {
            "basic_pay_php": salary,
            "estimated_daily_rate": round(salary / 30, 2) if salary else 0,
            "vl_encashment_value": round((salary / 30) * vacation, 2) if salary else 0,
        },
        "attendance": {"present_days": 21, "late_days": 1, "remote_days": 4},
        "performance": {"pulse": "Stable", "manager_signal": "On track", "risk": "Low"},
        "onboarding": onboarding_tasks(employee),
    }


def recruitment_pipeline() -> List[Dict[str, Any]]:
    return [
        {"name": "Maya Chen", "role": "People Operations Lead", "stage": "Interview", "score": 91, "skills": ["HRIS", "Payroll", "Analytics"]},
        {"name": "Dev Sharma", "role": "Technical Recruiter", "stage": "Screening", "score": 84, "skills": ["Sourcing", "ATS", "Scheduling"]},
        {"name": "Ava Morgan", "role": "HR Generalist", "stage": "Offer", "score": 88, "skills": ["Employee Relations", "Policy", "Onboarding"]},
        {"name": "Luis Reyes", "role": "Talent Coordinator", "stage": "Applied", "score": 76, "skills": ["Coordination", "CRM", "Reporting"]},
    ]


def analyze_resume_text(text: str, role: str = "HR Generalist") -> Dict[str, Any]:
    words = re.findall(r"[A-Za-z][A-Za-z+#.-]+", text.lower())
    token_set = set(words)
    skill_bank = {
        "recruiting", "sourcing", "interviewing", "onboarding", "payroll", "analytics",
        "excel", "python", "hris", "workday", "policy", "compliance", "benefits",
        "employee", "relations", "leadership", "reporting",
    }
    skills = sorted({skill for skill in skill_bank if skill in token_set})
    years = [int(y) for y in re.findall(r"(\d+)\+?\s+years?", text.lower())]
    experience = max(years) if years else 0
    score = min(98, 55 + len(skills) * 5 + min(experience, 10) * 2)
    return {
        "target_role": role,
        "ats_score": score,
        "skills": skills[:10],
        "experience_years": experience,
        "summary": f"Candidate shows {len(skills)} relevant HR signals for {role}.",
        "recommendation": "Advance to structured interview" if score >= 75 else "Keep warm and request more detail",
    }


def admin_insights() -> Dict[str, Any]:
    metrics = workforce_metrics()
    low_leave_count = len(metrics["low_leave_alerts"])
    return {
        **metrics,
        "retention_indicator": "Healthy" if low_leave_count <= 1 else "Watch",
        "burnout_indicator": "Elevated" if low_leave_count >= 2 else "Normal",
        "ai_summary": (
            f"{metrics['total_employees']} employees across "
            f"{len(metrics['department_counts'])} departments. "
            f"Average leave balance is {metrics['avg_vacation_leave']} VL and "
            f"{metrics['avg_sick_leave']} SL days."
        ),
    }


def workflow_events() -> List[Dict[str, str]]:
    return [
        {"step": "Resume uploaded", "agent": "Recruitment Agent", "status": "Extracted profile and skills"},
        {"step": "Candidate scored", "agent": "Recruitment Agent", "status": "ATS fit score generated"},
        {"step": "HR notified", "agent": "Analytics Agent", "status": "Hiring signal sent to dashboard"},
        {"step": "Interview scheduled", "agent": "Onboarding Agent", "status": "Calendar-ready handoff"},
        {"step": "Offer to onboarding", "agent": "Employee Support Agent", "status": "Tasks prepared"},
    ]


def knowledge_recommendations(query: str = "") -> List[Dict[str, str]]:
    q = query.lower()
    policies = [
        {"title": "Vacation leave eligibility", "type": "Policy", "signal": "High"},
        {"title": "Sick leave carry-over", "type": "Policy", "signal": "Medium"},
        {"title": "Probation and regularization", "type": "Handbook", "signal": "High"},
        {"title": "Leave encashment calculation", "type": "Payroll", "signal": "Medium"},
    ]
    if not q:
        return policies
    return [p for p in policies if any(part in p["title"].lower() for part in q.split())] or policies[:2]
