"""Two inbox sources: (1) static demo JSON, (2) live Gmail via IMAP."""
import json, os, email as email_lib, imaplib
from email.header import decode_header
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def load_demo_inbox() -> list[dict]:
    """Load the bundled 10 seed emails. Always works, no setup."""
    path = Path(__file__).parent / "data" / "demo_emails.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _decode(value):
    if value is None: return ""
    parts = decode_header(value)
    out = ""
    for text, enc in parts:
        if isinstance(text, bytes):
            try: out += text.decode(enc or "utf-8", errors="ignore")
            except: out += text.decode("utf-8", errors="ignore")
        else:
            out += text
    return out


def load_gmail_inbox(limit: int = 10) -> list[dict]:
    """Pull the latest `limit` emails from Gmail via IMAP App Password."""
    addr = os.getenv("GMAIL_ADDRESS")
    pw   = os.getenv("GMAIL_APP_PASSWORD")
    if not addr or not pw:
        raise RuntimeError("Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in .env")

    M = imaplib.IMAP4_SSL("imap.gmail.com")
    M.login(addr, pw)
    M.select("INBOX")
    _, data = M.search(None, "ALL")
    ids = data[0].split()[-limit:][::-1]  # newest first

    out = []
    for i, msg_id in enumerate(ids):
        _, msg_data = M.fetch(msg_id, "(RFC822)")
        msg = email_lib.message_from_bytes(msg_data[0][1])
        subj = _decode(msg["Subject"])
        frm  = _decode(msg.get("From", ""))
        date = _decode(msg.get("Date", ""))
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break
                    except: pass
        else:
            try: body = msg.get_payload(decode=True).decode(errors="ignore")
            except: body = str(msg.get_payload())

        # parse "Name <email>"
        name, email_addr = frm, frm
        if "<" in frm and ">" in frm:
            name = frm.split("<")[0].strip().strip('"')
            email_addr = frm.split("<")[1].split(">")[0].strip()

        out.append({
            "id": f"g{i}",
            "from_name": name or email_addr,
            "from_email": email_addr,
            "subject": subj,
            "body": (body or "")[:1500],
            "received": date,
            "thread_length": 1,
            "has_attachment": False,
        })
    M.logout()
    return out
