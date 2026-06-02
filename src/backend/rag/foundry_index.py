"""Azure AI Foundry RAG index — retrieves user's past correspondence."""
from typing import List
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential


class FoundryRAG:
    def __init__(self, foundry_endpoint: str, index_name: str):
        self.endpoint = foundry_endpoint
        self.index_name = index_name
        self._client = None

    async def _get_client(self):
        if self._client is None:
            self._client = AIProjectClient(
                endpoint=self.endpoint,
                credential=DefaultAzureCredential(),
            )
        return self._client

    async def retrieve(self, user_id: str, query: str, k: int = 8) -> List[str]:
        """Hybrid (BM25 + vector) retrieval scoped to a single user."""
        client = await self._get_client()
        search = await client.indexes.search(
            index_name=self.index_name,
            query=query,
            filter=f"user_id eq '{user_id}'",
            top=k,
            query_type="semantic_hybrid",
        )
        return [hit["content"] for hit in search["results"]]
