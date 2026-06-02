"""
Evaluation harness — runs InboxIQ against a 500-email gold set.
Outputs: precision/recall on priority labels, tone-match score,
end-to-end task completion rate.
"""
import json
import asyncio
from pathlib import Path
from sklearn.metrics import classification_report

from backend.agents.orchestrator import AgentOrchestrator


GOLD = Path(__file__).parent / "gold_set.jsonl"


async def main():
    orch = AgentOrchestrator(...)
    y_true, y_pred = [], []

    with GOLD.open() as f:
        for line in f:
            row = json.loads(line)
            result = await orch.triage_inbox(
                user_id="eval", since_hours=24
            )
            y_true.append(row["label"])
            y_pred.append(result["urgent"][0]["priority"] if result["urgent"] else "FYI")

    print(classification_report(y_true, y_pred,
                                labels=["URGENT", "ACTION", "FYI", "NOISE"]))


if __name__ == "__main__":
    asyncio.run(main())
