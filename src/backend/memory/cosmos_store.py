"""Cosmos DB agent memory + immutable audit log."""
from azure.cosmos.aio import CosmosClient
from datetime import datetime, timezone
import uuid
import json


class CosmosMemory:
    def __init__(self, conn_str: str):
        self.client = CosmosClient.from_connection_string(conn_str)
        self.db = self.client.get_database_client("inboxiq")
        self.events = self.db.get_container_client("events")

    async def log_event(self, user_id: str, event_type: str, payload: dict):
        await self.events.create_item({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "type": event_type,
            "payload": json.loads(json.dumps(payload, default=str)),
            "ts": datetime.now(timezone.utc).isoformat(),
        })
