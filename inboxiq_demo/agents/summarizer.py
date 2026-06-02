"""Summarizer Agent — collapses each email into ONE crisp sentence."""
from .llm import chat

SYSTEM = """You are a ruthless summarizer. Compress the email below into
ONE sentence (max 22 words) that captures:
- Who sent it
- What they want or are telling the user
- Any explicit deadline

Write in third person, present tense. No fluff. No greeting. No sign-off."""

def summarize(email: dict) -> str:
    user_msg = f"""From: {email['from_name']}
Subject: {email['subject']}
Body:
{email['body']}"""
    return chat(SYSTEM, user_msg, temperature=0.1, max_tokens=80)
