"""Drafter Agent — produces 3 context-aware reply options."""
from .llm import chat
import json, re

SYSTEM = """You draft email replies on behalf of Alex Chen, a Director of Product
at Acme Corp. Tone: warm but concise, executive-level, no corporate fluff.
Sign off as 'Alex'.

Produce EXACTLY 3 reply options:
1. "concise" — 1-2 sentences, fastest acknowledgment
2. "detailed" — 3-5 sentences, addresses every point raised
3. "decline_or_defer" — politely pushes back, delegates, or asks for more info

Return ONLY valid JSON: {"concise": "...", "detailed": "...", "decline_or_defer": "..."}"""

def draft(email: dict) -> dict:
    user_msg = f"""Incoming email to reply to:

From: {email['from_name']} <{email['from_email']}>
Subject: {email['subject']}
Body:
{email['body']}"""
    raw = chat(SYSTEM, user_msg, temperature=0.4, max_tokens=700)
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {"concise": raw, "detailed": "", "decline_or_defer": ""}
    try:
        return json.loads(match.group(0))
    except Exception:
        return {"concise": raw, "detailed": "", "decline_or_defer": ""}
