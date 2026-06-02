"""Classifier agent — tags each email with priority + intent."""
import json
from typing import List, Dict

CLASSIFIER_SYSTEM = """You are an expert email classifier embedded in the InboxIQ
agentic system. For every email you receive, output a strict JSON object:

{
  "id": "<email_id>",
  "priority": "URGENT" | "ACTION" | "FYI" | "NOISE",
  "intent": "request" | "question" | "fyi" | "scheduling" | "approval" | "other",
  "summary": "<one sentence, <=20 words>",
  "deadline": "<ISO-8601 or null>",
  "people": ["<name1>", "<name2>"]
}

Rules:
- URGENT: explicit time pressure (<24h) AND business-critical.
- ACTION: requires a reply or task from the user.
- FYI: informational only.
- NOISE: newsletters, automated notifications.
Never invent deadlines. If unsure, return null.
"""


async def classify_emails(classifier_agent, emails: List[Dict]) -> List[Dict]:
    """Run the classifier agent over each email; parallelize for speed."""
    import asyncio

    async def _one(email):
        prompt = json.dumps({
            "id": email["id"],
            "from": email["from"],
            "subject": email["subject"],
            "body": email["body"][:2000],
            "received": email["received_at"],
        })
        result = await classifier_agent.run(task=prompt)
        try:
            return json.loads(result.messages[-1].content)
        except json.JSONDecodeError:
            return {
                "id": email["id"], "priority": "FYI",
                "intent": "other", "summary": email["subject"],
                "deadline": None, "people": [],
            }

    return await asyncio.gather(*[_one(e) for e in emails])
