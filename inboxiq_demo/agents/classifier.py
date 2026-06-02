"""Classifier Agent — labels each email Urgent / Action / FYI / Noise."""
from .llm import chat

SYSTEM = """You are an email triage classifier for a busy executive.
Classify each email into EXACTLY ONE of these four categories:

- URGENT: Time-sensitive, blocks revenue/legal/customer, needs reply today
- ACTION: Requires a decision, approval, or substantive reply within 1-2 days
- FYI: Informational only, no reply needed, just keep the user aware
- NOISE: Marketing, notifications, automated receipts, newsletters — auto-archive

Also return:
- priority_score: integer 1 (lowest) to 10 (highest)
- reason: one short sentence explaining the label
- mentions_user: true if the email expects a reply from the recipient

Respond ONLY in valid JSON with keys: label, priority_score, reason, mentions_user."""

import json, re

def classify(email: dict) -> dict:
    user_msg = f"""From: {email['from_name']} <{email['from_email']}>
Subject: {email['subject']}
Body:
{email['body']}"""
    raw = chat(SYSTEM, user_msg, temperature=0.0, max_tokens=200)
    # Extract JSON even if model adds prose around it
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {"label": "FYI", "priority_score": 3, "reason": "could not parse", "mentions_user": False}
    try:
        data = json.loads(match.group(0))
        data["label"] = data.get("label", "FYI").upper()
        return data
    except Exception:
        return {"label": "FYI", "priority_score": 3, "reason": "parse error", "mentions_user": False}
