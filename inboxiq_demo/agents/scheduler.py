"""Scheduler Agent — detects meeting intent and proposes time slots."""
from .llm import chat
import json, re

SYSTEM = """Detect if the email is requesting a meeting, call, or sync.
If YES, propose 3 reasonable time slots in the next 5 business days
(business hours 9am-6pm IST, avoid 12-1pm lunch, default 30 min unless
the email implies longer).

Return ONLY JSON:
{"is_meeting_request": true/false,
 "proposed_slots": ["...", "...", "..."],
 "duration_min": 30,
 "title": "..."}

If not a meeting request, return {"is_meeting_request": false, "proposed_slots": [], "duration_min": 0, "title": ""}.

Today is Tuesday, June 2, 2026."""

def schedule(email: dict) -> dict:
    user_msg = f"From: {email['from_name']}\nSubject: {email['subject']}\nBody:\n{email['body']}"
    raw = chat(SYSTEM, user_msg, temperature=0.1, max_tokens=300)
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {"is_meeting_request": False, "proposed_slots": [], "duration_min": 0, "title": ""}
    try:
        return json.loads(match.group(0))
    except Exception:
        return {"is_meeting_request": False, "proposed_slots": [], "duration_min": 0, "title": ""}
