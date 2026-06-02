"""
InboxIQ — FastAPI Entrypoint
Microsoft Build AI 2026 Hackathon
Theme 01: AI at Work
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

from agents.orchestrator import AgentOrchestrator
from rag.foundry_index import FoundryRAG
from memory.cosmos_store import CosmosMemory

load_dotenv()

app = FastAPI(
    title="InboxIQ API",
    description="Agentic workplace productivity assistant on the Microsoft AI Stack",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Singletons ----------
orchestrator = AgentOrchestrator(
    openai_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    openai_key=os.environ["AZURE_OPENAI_KEY"],
    deployment="gpt-4o",
)
rag = FoundryRAG(
    foundry_endpoint=os.environ["AZURE_FOUNDRY_ENDPOINT"],
    index_name="user-correspondence",
)
memory = CosmosMemory(conn_str=os.environ["COSMOS_CONNECTION_STRING"])


# ---------- Schemas ----------
class TriageRequest(BaseModel):
    user_id: str
    since_hours: int = 24


class DraftRequest(BaseModel):
    user_id: str
    email_id: str
    intent: Optional[str] = None  # "accept", "decline", "ask_followup", etc.


class BriefingResponse(BaseModel):
    summary: str
    urgent_count: int
    action_items: List[str]
    meetings_today: List[dict]
    audio_url: Optional[str]


# ---------- Routes ----------
@app.get("/health")
def health():
    return {"status": "ok", "service": "inboxiq", "version": "1.0.0"}


@app.post("/triage")
async def triage(req: TriageRequest):
    """Run full agent loop: classify -> summarize -> rank inbox."""
    try:
        result = await orchestrator.triage_inbox(
            user_id=req.user_id, since_hours=req.since_hours
        )
        await memory.log_event(req.user_id, "triage", result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/draft")
async def draft_reply(req: DraftRequest):
    """Generate a context-grounded reply draft. Requires human approval."""
    context = await rag.retrieve(user_id=req.user_id, query=req.email_id, k=8)
    draft = await orchestrator.draft_reply(
        email_id=req.email_id, intent=req.intent, context=context
    )
    return {"draft": draft, "requires_approval": True}


@app.get("/briefing/{user_id}", response_model=BriefingResponse)
async def morning_briefing(user_id: str):
    """Compile the daily 60-second briefing."""
    briefing = await orchestrator.daily_briefing(user_id=user_id)
    return briefing


@app.post("/approve/{action_id}")
async def approve_action(action_id: str, user_id: str):
    """Human-in-the-loop approval for outbound writes."""
    return await orchestrator.execute_approved_action(action_id, user_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
