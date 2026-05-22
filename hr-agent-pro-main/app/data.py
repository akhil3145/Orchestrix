"""Data access helpers for the demo HR operating system."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, List

import pandas as pd

from app.config import settings


@lru_cache(maxsize=4)
def load_employees(path: str = settings.data_path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for column in ["vacation_leave", "sick_leave", "basic_pay_in_php"]:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)
    return df


def employee_names() -> List[str]:
    return load_employees()["name"].dropna().astype(str).tolist()


def get_employee(name: str) -> Dict[str, Any]:
    df = load_employees()
    match = df[df["name"].str.lower() == name.lower()]
    if match.empty:
        return {}
    return match.iloc[0].to_dict()


def workforce_metrics() -> Dict[str, Any]:
    df = load_employees()
    total = len(df)
    avg_vacation = round(float(df["vacation_leave"].mean()), 1) if total else 0
    avg_sick = round(float(df["sick_leave"].mean()), 1) if total else 0
    payroll_total = int(df["basic_pay_in_php"].sum()) if "basic_pay_in_php" in df else 0
    low_leave = df[(df["vacation_leave"] < 5) | (df["sick_leave"] < 3)]
    return {
        "total_employees": total,
        "avg_vacation_leave": avg_vacation,
        "avg_sick_leave": avg_sick,
        "monthly_payroll_php": payroll_total,
        "department_counts": df["organizational_unit"].value_counts().to_dict(),
        "status_counts": df["employment_status"].value_counts().to_dict(),
        "rank_counts": df["rank"].value_counts().to_dict(),
        "low_leave_alerts": low_leave[["name", "vacation_leave", "sick_leave"]].to_dict("records"),
    }


def onboarding_tasks(employee: Dict[str, Any]) -> List[Dict[str, Any]]:
    status = str(employee.get("employment_status", "")).lower()
    probation = status == "probation"
    return [
        {"task": "Complete profile verification", "owner": "Employee", "done": True},
        {"task": "Review leave and attendance policy", "owner": "HR", "done": not probation},
        {"task": "Manager 30-day check-in", "owner": employee.get("supervisor") or "HR", "done": False},
        {"task": "Benefits enrollment", "owner": "People Ops", "done": not probation},
    ]


def hr_requests(employee: Dict[str, Any]) -> List[Dict[str, str]]:
    return [
        {"type": "Leave request", "status": "Ready", "detail": f"{employee.get('vacation_leave', 0)} VL days available"},
        {"type": "Document request", "status": "2 day SLA", "detail": "Certificate of employment"},
        {"type": "Manager approval", "status": "Pending", "detail": employee.get("supervisor") or "Unassigned"},
    ]
