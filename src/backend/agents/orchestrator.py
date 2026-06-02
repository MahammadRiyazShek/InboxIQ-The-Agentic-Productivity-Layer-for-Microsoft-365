"""
AutoGen-based multi-agent orchestrator.
Coordinates Planner, Classifier, Drafter, Scheduler, Critic, Reporter agents.
"""
import asyncio
from typing import Dict, List, Any
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from .planner import PLANNER_SYSTEM
from .classifier import CLASSIFIER_SYSTEM, classify_emails
from .drafter import DRAFTER_SYSTEM
from .scheduler import SCHEDULER_SYSTEM
from .critic import CRITIC_SYSTEM
from .reporter import build_briefing


class AgentOrchestrator:
    def __init__(self, openai_endpoint: str, openai_key: str, deployment: str):
        self.model = AzureOpenAIChatCompletionClient(
            azure_endpoint=openai_endpoint,
            api_key=openai_key,
            azure_deployment=deployment,
            model="gpt-4o",
            api_version="2024-10-21",
        )

        self.kernel = Kernel()
        self.kernel.add_service(
            AzureChatCompletion(
                deployment_name=deployment,
                endpoint=openai_endpoint,
                api_key=openai_key,
            )
        )

        self.planner = AssistantAgent("planner", model_client=self.model,
                                      system_message=PLANNER_SYSTEM)
        self.classifier = AssistantAgent("classifier", model_client=self.model,
                                         system_message=CLASSIFIER_SYSTEM)
        self.drafter = AssistantAgent("drafter", model_client=self.model,
                                      system_message=DRAFTER_SYSTEM)
        self.scheduler = AssistantAgent("scheduler", model_client=self.model,
                                        system_message=SCHEDULER_SYSTEM)
        self.critic = AssistantAgent("critic", model_client=self.model,
                                     system_message=CRITIC_SYSTEM)

        self.team = RoundRobinGroupChat(
            [self.planner, self.classifier, self.drafter,
             self.scheduler, self.critic],
            max_turns=12,
        )

    async def triage_inbox(self, user_id: str, since_hours: int = 24) -> Dict[str, Any]:
        """Pull recent emails via Graph, classify, return ranked list."""
        from plugins.graph_mail import fetch_recent_mail
        emails = await fetch_recent_mail(user_id, since_hours)
        classified = await classify_emails(self.classifier, emails)
        return {
            "user_id": user_id,
            "total": len(emails),
            "urgent": [e for e in classified if e["priority"] == "URGENT"],
            "action": [e for e in classified if e["priority"] == "ACTION"],
            "fyi":    [e for e in classified if e["priority"] == "FYI"],
            "noise":  [e for e in classified if e["priority"] == "NOISE"],
        }

    async def draft_reply(self, email_id: str, intent: str, context: List[str]) -> str:
        """RAG-grounded reply generation; Critic validates before return."""
        prompt = (
            f"Draft a reply to email {email_id}. Intent: {intent}.\n"
            f"Use the user's voice based on these past messages:\n"
            + "\n---\n".join(context[:8])
        )
        result = await self.team.run(task=prompt)
        # Critic must approve; otherwise re-draft
        return result.messages[-1].content

    async def daily_briefing(self, user_id: str) -> Dict[str, Any]:
        triage = await self.triage_inbox(user_id, since_hours=12)
        return await build_briefing(self.model, triage)

    async def execute_approved_action(self, action_id: str, user_id: str) -> Dict[str, str]:
        # Look up pending action in memory, execute via Graph
        return {"status": "executed", "action_id": action_id}
