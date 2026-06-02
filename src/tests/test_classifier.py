import pytest
from backend.agents.classifier import classify_emails


class FakeAgent:
    async def run(self, task):
        class M: content = '{"id":"1","priority":"URGENT","intent":"request","summary":"Need quote by EOD","deadline":null,"people":["John"]}'
        class R: messages = [M()]
        return R()


@pytest.mark.asyncio
async def test_classifier_returns_json():
    out = await classify_emails(FakeAgent(), [{
        "id": "1", "from": "j@x.com", "subject": "Quote",
        "body": "Need by EOD", "received_at": "2026-06-01T10:00Z"
    }])
    assert out[0]["priority"] == "URGENT"
