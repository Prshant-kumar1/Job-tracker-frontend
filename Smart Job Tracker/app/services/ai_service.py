"""
Gemini-powered AI suggestion engine with rule-based fallback.

This module is intentionally isolated from the route layer so it can later
be swapped for a different LLM call (OpenAI / Claude) without touching
any routing or DB logic — only this function's internals would change,
and the function signature (JobApplication in, suggestion string out)
would stay the same.
"""
import os
import logging
from datetime import date
from typing import Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

from app.config import settings
from app.models import JobApplication, ApplicationStatus

logger = logging.getLogger(__name__)

# Initialize Gemini if API key is available
if GEMINI_AVAILABLE and settings.GEMINI_API_KEY:
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel("gemini-flash-latest")
        # Test the model
        _gemini_model.generate_content("test")
        logger.info("Gemini AI initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize Gemini: {e}")
        _gemini_model = None
else:
    _gemini_model = None
    if not GEMINI_AVAILABLE:
        logger.info("google-generativeai not installed, using rule-based suggestions")
    elif not settings.GEMINI_API_KEY:
        logger.info("GEMINI_API_KEY not set, using rule-based suggestions")

# Rough mapping of role keywords -> relevant prep topics, used to make
# suggestions feel tailored to the specific role rather than generic.
ROLE_TOPIC_HINTS = {
    "backend": "FastAPI/Django fundamentals, REST API design, and SQL joins",
    "frontend": "React component design, state management, and accessibility basics",
    "full stack": "end-to-end feature design across the frontend and backend",
    "data": "SQL, data cleaning, and basic statistics",
    "ml": "core ML concepts, model evaluation metrics, and a recent project walkthrough",
    "ai": "LLM/agent fundamentals and a recent project walkthrough",
    "android": "Kotlin/Java fundamentals and Android lifecycle concepts",
    "devops": "CI/CD pipelines, containers, and basic cloud networking",
    "qa": "test case design and common testing frameworks",
}


def _topic_hint_for_role(role: str) -> str:
    role_lower = role.lower()
    for keyword, hint in ROLE_TOPIC_HINTS.items():
        if keyword in role_lower:
            return hint
    return "your core CS fundamentals (DSA, OOP, DBMS, OS) and one strong project walkthrough"


def _days_since(target: Optional[date]) -> Optional[int]:
    if target is None:
        return None
    return (date.today() - target).days


def _build_prompt(application: JobApplication) -> str:
    """Build a detailed prompt for Gemini based on application details."""
    company = application.company
    role = application.role
    status = application.status.value
    topic_hint = _topic_hint_for_role(role)
    days_applied = _days_since(application.date_applied)
    days_to_followup = (
        (application.follow_up_date - date.today()).days
        if application.follow_up_date
        else None
    )
    notes = application.notes.strip() if application.notes else "No notes provided."

    prompt = f"""You are an expert career coach helping a job seeker with their application tracking.

Application Details:
- Company: {company}
- Role: {role}
- Current Status: {status}
- Days Since Applied: {days_applied if days_applied is not None else "Unknown"}
- Days Until Follow-up: {days_to_followup if days_to_followup is not None else "Not set"}
- Notes: {notes}

Role-Specific Focus Area: {topic_hint}

Provide a concise, actionable next-step suggestion (2-3 sentences max) tailored to this specific situation. Be encouraging but practical. Focus on what they should do THIS WEEK."""
    return prompt


def _generate_with_gemini(application: JobApplication) -> Optional[str]:
    """Generate suggestion using Gemini API."""
    if _gemini_model is None:
        return None
    
    try:
        prompt = _build_prompt(application)
        response = _gemini_model.generate_content(prompt)
        suggestion = response.text.strip()
        
        if suggestion:
            logger.info(f"Gemini suggestion generated for application {application.id}")
            return suggestion
    except Exception as e:
        logger.error(f"Gemini API error for application {application.id}: {e}")
    
    return None


def _generate_rule_based(application: JobApplication) -> str:
    """Fallback rule-based suggestion (original logic)."""
    company = application.company
    role = application.role
    status = application.status
    topic_hint = _topic_hint_for_role(role)
    days_applied = _days_since(application.date_applied)
    days_to_followup = (
        (application.follow_up_date - date.today()).days
        if application.follow_up_date
        else None
    )

    if status == ApplicationStatus.APPLIED:
        if days_applied is None:
            timing = "Since there's no applied date on file, set one so we can time your follow-up properly."
        elif days_applied < 4:
            timing = (
                f"You applied {days_applied} day(s) ago, so it's still early — "
                "give it a few more days before reaching out."
            )
        else:
            timing = (
                f"It's been {days_applied} days since you applied, which is a good window "
                "to send a polite follow-up email to the recruiter or hiring manager."
            )
        return (
            f"You applied for the {role} role at {company}. {timing} "
            f"In the meantime, use the wait time to brush up on {topic_hint}."
        )

    if status == ApplicationStatus.OA:
        return (
            f"Your online assessment for the {role} role at {company} is the next hurdle. "
            "Spend the next few days on timed DSA practice (arrays, strings, trees, graphs), "
            "a quick pass on aptitude/MCQ-style questions, and a refresher on "
            f"{topic_hint}. Treat it like a real exam: simulate the time limit at least once."
        )

    if status == ApplicationStatus.INTERVIEW:
        followup_note = (
            f"Your next follow-up is in {days_to_followup} day(s) — keep that date in mind."
            if days_to_followup is not None and days_to_followup >= 0
            else "If you don't have one yet, set a follow-up date so this doesn't slip."
        )
        return (
            f"You have an interview stage for the {role} role at {company}. "
            f"Research the company's products and recent news, prepare a 2-3 minute walkthrough "
            f"of your strongest project, and revise {topic_hint}. {followup_note}"
        )

    if status == ApplicationStatus.REJECTED:
        notes_line = (
            f" Your notes mention: \"{application.notes.strip()[:120]}\" — "
            "worth revisiting before your next application."
            if application.notes
            else " Consider jotting down what you think went wrong while it's fresh."
        )
        return (
            f"The {role} application at {company} didn't work out this time, and that's okay — "
            "it happens to almost everyone. Take a few minutes to write down what you'd do "
            f"differently next time.{notes_line} Then redirect that energy into applying to "
            "a couple of similar roles this week rather than dwelling on this one."
        )

    if status == ApplicationStatus.OFFER:
        return (
            f"Congratulations on the offer for the {role} role at {company}! "
            "Before accepting, compare it against your other options on stipend/CTC, "
            "location and remote flexibility, the learning curve and tech stack, and the "
            "team you'd be joining. Make sure you also note the joining date and any "
            "documents you need to submit."
        )

    # Fallback for any unexpected status value
    return (
        f"No specific guidance is available for the current status of your {role} "
        f"application at {company}. Double-check the status value is correct."
    )


def generate_suggestion(application: JobApplication) -> str:
    """
    Build a natural-language next-step suggestion for a single application,
    based on its status, company, role, dates, and notes.
    
    Uses Gemini API if available and configured, otherwise falls back to rule-based logic.
    """
    # Try Gemini first
    gemini_suggestion = _generate_with_gemini(application)
    if gemini_suggestion:
        return gemini_suggestion
    
    # Fallback to rule-based
    logger.info(f"Using rule-based suggestion for application {application.id}")
    return _generate_rule_based(application)
