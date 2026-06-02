"""Microsoft Graph plugin — Outlook mail access."""
import os
import httpx
from datetime import datetime, timedelta, timezone
from msal import ConfidentialClientApplication


def _get_token() -> str:
    app = ConfidentialClientApplication(
        client_id=os.environ["GRAPH_CLIENT_ID"],
        client_credential=os.environ["GRAPH_CLIENT_SECRET"],
        authority=f"https://login.microsoftonline.com/{os.environ['GRAPH_TENANT_ID']}",
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" not in result:
        raise RuntimeError(f"Token acquisition failed: {result}")
    return result["access_token"]


async def fetch_recent_mail(user_id: str, since_hours: int = 24):
    """Fetch the user's recent mail via Microsoft Graph."""
    token = _get_token()
    since = (datetime.now(timezone.utc) - timedelta(hours=since_hours)).isoformat()
    url = (
        f"https://graph.microsoft.com/v1.0/users/{user_id}/messages"
        f"?$filter=receivedDateTime ge {since}"
        f"&$select=id,subject,from,bodyPreview,receivedDateTime"
        f"&$top=200&$orderby=receivedDateTime desc"
    )
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url, headers={"Authorization": f"Bearer {token}"})
        r.raise_for_status()
        data = r.json().get("value", [])

    return [
        {
            "id": m["id"],
            "from": m["from"]["emailAddress"]["address"],
            "subject": m["subject"],
            "body": m["bodyPreview"],
            "received_at": m["receivedDateTime"],
        }
        for m in data
    ]
