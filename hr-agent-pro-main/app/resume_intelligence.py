"""Resume extraction, analysis, scoring, ranking, and report generation."""

from __future__ import annotations

import io
import re
from collections import Counter
from typing import Any, Dict, Iterable, List


SKILL_TAXONOMY = {
    "recruiting": ["recruiting", "recruitment", "sourcing", "talent acquisition", "headhunting"],
    "interviewing": ["interview", "interviewing", "screening", "assessment"],
    "ats": ["ats", "greenhouse", "lever", "workable", "icims", "bamboohr"],
    "hr operations": ["hr operations", "hris", "workday", "payroll", "benefits", "onboarding"],
    "employee relations": ["employee relations", "grievance", "engagement", "people operations"],
    "analytics": ["analytics", "dashboard", "reporting", "excel", "sql", "python", "power bi", "tableau"],
    "compliance": ["compliance", "policy", "labor", "audit", "documentation"],
    "leadership": ["leadership", "managed", "led", "mentored", "stakeholder"],
    "communication": ["communication", "presentation", "facilitation", "negotiation"],
    "project management": ["project management", "roadmap", "program", "process improvement"],
}

ROLE_KEYWORDS = {
    "HR Generalist": ["hr operations", "employee relations", "compliance", "benefits", "onboarding"],
    "Technical Recruiter": ["recruiting", "sourcing", "interviewing", "ats", "analytics"],
    "People Operations Lead": ["leadership", "hr operations", "analytics", "employee relations", "project management"],
    "Talent Coordinator": ["ats", "communication", "scheduling", "recruiting", "onboarding"],
}


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes using pypdf when available."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("PDF support requires pypdf. Install dependencies from requirements.txt.") from exc

    reader = PdfReader(io.BytesIO(file_bytes))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages).strip()


def extract_text_from_upload(file_bytes: bytes, filename: str) -> str:
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if suffix == "pdf":
        return extract_text_from_pdf(file_bytes)
    if suffix in {"txt", "md"}:
        return file_bytes.decode("utf-8", errors="ignore")
    raise ValueError("Unsupported resume format. Upload a PDF or plain text resume.")


def detect_candidate_name(text: str, fallback: str = "Candidate") -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines[:8]:
        if 2 <= len(line.split()) <= 4 and not any(ch.isdigit() for ch in line):
            if not re.search(r"resume|curriculum|email|phone|linkedin", line, re.IGNORECASE):
                return line[:80]
    clean = re.sub(r"[_-]+", " ", fallback.rsplit(".", 1)[0]).strip()
    return clean.title() if clean else "Candidate"


def detect_skills(text: str) -> List[Dict[str, Any]]:
    normalized = re.sub(r"\s+", " ", text.lower())
    detected = []
    for skill, aliases in SKILL_TAXONOMY.items():
        hits = [alias for alias in aliases if alias in normalized]
        if hits:
            detected.append({"skill": skill, "evidence": hits[:3], "weight": len(hits)})
    return sorted(detected, key=lambda item: (-item["weight"], item["skill"]))


def _years_of_experience(text: str) -> int:
    years = [int(match) for match in re.findall(r"(\d{1,2})\+?\s+(?:years|yrs)", text.lower())]
    date_ranges = re.findall(r"(20\d{2}|19\d{2})\s*[-–]\s*(20\d{2}|present|current)", text.lower())
    for start, end in date_ranges:
        end_year = 2026 if end in {"present", "current"} else int(end)
        years.append(max(0, end_year - int(start)))
    return min(max(years) if years else 0, 40)


def _experience_overview(text: str, years: int) -> str:
    seniority = "early-career"
    if years >= 8:
        seniority = "senior"
    elif years >= 4:
        seniority = "mid-level"
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    useful = [s.strip() for s in sentences if 60 <= len(s.strip()) <= 220]
    detail = useful[0] if useful else "Resume contains relevant HR and recruiting signals."
    return f"{seniority.title()} profile with approximately {years} years of stated experience. {detail}"


def _role_match_score(role: str, skills: Iterable[Dict[str, Any]]) -> int:
    desired = set(ROLE_KEYWORDS.get(role, ROLE_KEYWORDS["HR Generalist"]))
    found = {item["skill"] for item in skills}
    if not desired:
        return 0
    return round(100 * len(desired & found) / len(desired))


def _keyword_density_score(text: str) -> int:
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    if not words:
        return 0
    counts = Counter(words)
    hr_terms = {
        "hiring", "recruiting", "recruitment", "sourcing", "screening", "interview",
        "interviewing", "ats", "employee", "policy", "payroll", "onboarding",
        "analytics", "compliance", "stakeholder", "reporting",
    }
    hits = sum(counts[term] for term in hr_terms)
    return min(100, hits * 8)


def analyze_resume(text: str, role: str = "HR Generalist", source_file: str = "") -> Dict[str, Any]:
    clean_text = re.sub(r"\s+", " ", text).strip()
    if len(clean_text) < 80:
        raise ValueError("Resume text is too short for reliable analysis.")

    candidate_name = detect_candidate_name(text, source_file)
    skills = detect_skills(clean_text)
    years = _years_of_experience(clean_text)
    role_score = _role_match_score(role, skills)
    keyword_score = _keyword_density_score(clean_text)
    experience_score = min(100, years * 10)
    structure_score = 85 if re.search(r"experience|education|skills|projects", clean_text, re.IGNORECASE) else 55
    ats_score = round((role_score * 0.40) + (experience_score * 0.25) + (keyword_score * 0.20) + (structure_score * 0.15))

    skill_names = [item["skill"] for item in skills]
    strengths = []
    if role_score >= 60:
        strengths.append("Strong alignment with target role keywords and responsibilities.")
    if years >= 5:
        strengths.append("Meaningful experience depth for HR workflow ownership.")
    if "analytics" in skill_names:
        strengths.append("Shows analytics/reporting signals useful for modern people operations.")
    if "leadership" in skill_names:
        strengths.append("Leadership or stakeholder-management indicators are present.")
    if not strengths:
        strengths.append("Baseline HR signals are present and can be explored in screening.")

    concerns = []
    if role_score < 45:
        concerns.append("Role-specific skill coverage is limited for the selected position.")
    if years < 2:
        concerns.append("Experience depth appears light or is not clearly stated.")
    if structure_score < 70:
        concerns.append("Resume structure may be hard for ATS systems to parse cleanly.")
    if not concerns:
        concerns.append("No major resume concerns detected from the available text.")

    recommendation = "Advance to interview"
    if ats_score < 60:
        recommendation = "Hold for manual review"
    elif ats_score < 75:
        recommendation = "Screen before interview"

    return {
        "candidate_name": candidate_name,
        "target_role": role,
        "source_file": source_file,
        "summary": f"{candidate_name} appears to be a {role} candidate with {len(skill_names)} detected skill areas and an ATS score of {ats_score}.",
        "detected_skills": skills,
        "skills": skill_names,
        "experience_years": years,
        "experience_overview": _experience_overview(clean_text, years),
        "strengths": strengths,
        "possible_concerns": concerns,
        "ats_score": ats_score,
        "score_breakdown": {
            "role_match": role_score,
            "experience": experience_score,
            "keyword_density": keyword_score,
            "resume_structure": structure_score,
        },
        "recommendation": recommendation,
    }


def candidate_report_markdown(analysis: Dict[str, Any]) -> str:
    skills = ", ".join(analysis.get("skills", [])) or "No clear skills detected"
    strengths = "\n".join(f"- {item}" for item in analysis.get("strengths", []))
    concerns = "\n".join(f"- {item}" for item in analysis.get("possible_concerns", []))
    breakdown = analysis.get("score_breakdown", {})
    breakdown_lines = "\n".join(f"- {key.replace('_', ' ').title()}: {value}/100" for key, value in breakdown.items())
    return f"""# Candidate Intelligence Report

## Candidate
- Name: {analysis.get("candidate_name", "Candidate")}
- Target role: {analysis.get("target_role", "Unspecified")}
- Source file: {analysis.get("source_file") or "Manual input"}
- Recommendation: {analysis.get("recommendation", "Review")}

## ATS Score
**{analysis.get("ats_score", 0)}/100**

{breakdown_lines}

## Summary
{analysis.get("summary", "")}

## Experience Overview
{analysis.get("experience_overview", "")}

## Detected Skills
{skills}

## Strengths
{strengths}

## Possible Concerns
{concerns}
"""


def ranking_table(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for index, candidate in enumerate(candidates, start=1):
        analysis = candidate.get("analysis", {})
        rows.append(
            {
                "Rank": index,
                "Candidate": candidate["candidate_name"],
                "Role": candidate["target_role"],
                "ATS Score": candidate["ats_score"],
                "Recommendation": candidate["recommendation"],
                "Skills": ", ".join(analysis.get("skills", [])[:5]),
            }
        )
    return rows
