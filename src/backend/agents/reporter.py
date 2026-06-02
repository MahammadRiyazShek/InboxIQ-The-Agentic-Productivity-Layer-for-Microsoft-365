"""Reporter agent — compiles the daily 60-second briefing."""
from typing import Dict, Any


async def build_briefing(model_client, triage: Dict[str, Any]) -> Dict[str, Any]:
    """Compile a morning briefing from the triage result."""
    urgent = triage["urgent"]
    action = triage["action"]

    bullets = []
    for e in urgent[:3]:
        bullets.append(f"🔴 {e['summary']} (from {e.get('people',['?'])[0]})")
    for e in action[:4]:
        bullets.append(f"🟡 {e['summary']}")

    summary = (
        f"Good morning. You have {len(urgent)} urgent items and "
        f"{len(action)} actions today. {len(triage['fyi'])} FYIs "
        f"were auto-filed."
    )

    return {
        "summary": summary,
        "urgent_count": len(urgent),
        "action_items": bullets,
        "meetings_today": [],  # populated by Graph plugin
        "audio_url": None,     # filled by Azure Speech if user opted in
    }
