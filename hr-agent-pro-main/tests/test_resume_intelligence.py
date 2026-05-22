from pathlib import Path
import uuid


def test_resume_analysis_generates_required_sections():
    from app.resume_intelligence import analyze_resume

    text = """
    Priya Shah
    Senior Technical Recruiter with 6 years of experience in recruiting, sourcing,
    interview screening, ATS workflows, analytics dashboards, and stakeholder communication.
    Experience
    Led hiring programs using Greenhouse and Excel reporting for engineering teams.
    Skills
    Recruiting, sourcing, interviewing, ATS, analytics, communication.
    """
    analysis = analyze_resume(text, role="Technical Recruiter", source_file="priya.pdf")

    assert analysis["candidate_name"] == "Priya Shah"
    assert analysis["ats_score"] >= 70
    assert "summary" in analysis
    assert analysis["strengths"]
    assert analysis["possible_concerns"]
    assert "recruiting" in analysis["skills"]


def test_candidate_report_contains_score_and_recommendation():
    from app.resume_intelligence import analyze_resume, candidate_report_markdown

    analysis = analyze_resume(
        "Maya Chen\n8 years recruiting onboarding payroll analytics leadership policy compliance experience.",
        role="People Operations Lead",
        source_file="maya.txt",
    )
    report = candidate_report_markdown(analysis)

    assert "Candidate Intelligence Report" in report
    assert "ATS Score" in report
    assert analysis["recommendation"] in report


def test_candidate_history_persists_to_sqlite(monkeypatch):
    db_path = Path("data") / f"test-candidates-{uuid.uuid4().hex}.db"
    monkeypatch.setenv("CANDIDATE_DB_PATH", str(db_path))

    from app.candidate_store import list_candidate_history, save_candidate_analysis
    from app.resume_intelligence import analyze_resume

    try:
        text = "Ava Morgan\n5 years HR operations onboarding employee relations compliance policy reporting."
        analysis = analyze_resume(text, role="HR Generalist", source_file="ava.txt")
        candidate_id = save_candidate_analysis(analysis, text, "ava.txt")
        history = list_candidate_history()

        assert candidate_id >= 1
        assert history[0]["candidate_name"] == "Ava Morgan"
        assert history[0]["ats_score"] == analysis["ats_score"]
    finally:
        if db_path.exists():
            db_path.unlink()
