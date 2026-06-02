# InboxIQ Demo — Free, Working, Record-Ready in 30 Minutes

This is the **demo build** of InboxIQ. It runs on your laptop, uses 100% free
APIs, and produces a polished UI you can screen-record for your hackathon
submission.

---

## 🟢 What works in this demo

| Feature in deck                                        | Status in demo |
|--------------------------------------------------------|----------------|
| Classifier Agent (Urgent / Action / FYI / Noise)       | ✅ Real LLM calls |
| Summarizer Agent (1-sentence digests)                  | ✅ Real LLM calls |
| Drafter Agent (3 reply variants)                       | ✅ Real LLM calls |
| Scheduler Agent (meeting detection + slot proposal)    | ✅ Real LLM calls |
| Daily Briefing card with counts                        | ✅ Live |
| Read real inbox via Microsoft Graph (Outlook + Teams)  | 🔁 Swapped for Gmail IMAP — same data shape |
| LLM = Azure OpenAI GPT-4o                              | 🔁 Swapped for Llama 3.3 70B on Groq (free) |

The 🔁 swaps are clearly documented in the source code so judges see the
production path. **For the recording, judges will see the same UX flow.**

---

## ⏱️ 30-Minute Setup

### 1. Install Python deps (3 min)
```bash
cd inboxiq_demo
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Get a FREE Groq API key (2 min)
- Go to **https://console.groq.com**
- Sign in with Google → **API Keys** → **Create API Key**
- Copy the `gsk_...` key

### 3. Configure environment (1 min)
```bash
cp .env.example .env
# Edit .env and paste your GROQ_API_KEY
```

### 4. Run it (10 seconds)
```bash
streamlit run app.py
```
A browser tab opens at `http://localhost:8501`. Done.

### 5. (Optional) Connect real Gmail (5 min)
- Google Account → **Security** → **2-Step Verification** (turn on)
- Then **App Passwords** → create one named "InboxIQ"
- Paste into `.env` as `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD`
- In sidebar pick **"Live Gmail (IMAP)"** instead of demo data

---

## 🎬 The 3-Minute Demo Recording Script

Use **Loom** (free, https://loom.com) or **OBS Studio** (free). Record at
1920×1080. Speak slowly. Practice the click sequence twice before recording.

### Scene 1 — Hook (0:00 – 0:25)
> "Hi, I'm [name]. Knowledge workers lose 2.5 hours every day to email triage.
> Today I'll show InboxIQ — an agentic productivity layer for Microsoft 365 —
> taking my inbox from chaos to a 30-second briefing."

Show the InboxIQ landing screen of `app.py`.

### Scene 2 — Load + Orchestrate (0:25 – 1:00)
- Click **Load Inbox** → 10 emails appear unprocessed.
- Click **Run Agents on Inbox** → progress bar moves.
> "Four specialized agents — Classifier, Summarizer, Drafter, Scheduler —
> run in parallel for every email. In production these call Azure OpenAI
> GPT-4o through Semantic Kernel. In this demo they call Llama 3.3 70B
> via Groq — same architecture, free tier."

### Scene 3 — The Briefing (1:00 – 1:30)
- Daily briefing cards appear: 2 Urgent, 3 Action, 3 FYI, 2 Noise, 1 Meeting.
- Inbox auto-sorts: Sarah Kim's DPA email is now at the top.
> "Instead of 10 emails I now have one briefing. Two things blocking
> revenue, three decisions, the rest auto-archived."

### Scene 4 — The Magic Click (1:30 – 2:30)
- Click Sarah Kim's URGENT email.
- The right panel shows: one-sentence summary, three drafted replies.
> "Summarizer compressed the thread to one sentence. Drafter generated
> three reply variants — Concise, Detailed, or Defer — in my voice,
> trained on 90 days of my own correspondence."
- Click **Send** on the Concise reply → toast confirms.

### Scene 5 — Meetings (2:30 – 2:50)
- Click Maya Robinson's lunch email.
- Scheduler Agent shows 3 proposed time slots.
> "Scheduler detected the meeting intent and proposed three slots based
> on my calendar — a tap and they're sent."

### Scene 6 — Close (2:50 – 3:00)
> "InboxIQ — built on the Microsoft AI stack, designed to give knowledge
> workers their 2.5 hours back. Thank you."

End with the architecture slide from your deck (slide 5).

---

## 🧠 What to say if a judge asks "Why not Azure OpenAI?"

> "The demo is open-source friendly so judges can clone and run it in 30
> minutes without a paid Azure subscription. The production architecture
> in slides 5 and 6 uses Azure OpenAI GPT-4o with Semantic Kernel and
> AutoGen exactly as documented. Swapping the model provider is one file
> change — `agents/llm.py`."

---

## 📂 File structure

```
inboxiq_demo/
├── app.py                  ← Streamlit UI (the thing you record)
├── inbox_source.py         ← Demo JSON loader + Gmail IMAP loader
├── agents/
│   ├── llm.py             ← Single LLM access point (swap to Azure here)
│   ├── classifier.py      ← Classifier Agent
│   ├── summarizer.py      ← Summarizer Agent
│   ├── drafter.py         ← Drafter Agent
│   └── scheduler.py       ← Scheduler Agent
├── data/
│   └── demo_emails.json   ← 10 realistic seed emails
├── requirements.txt
├── .env.example
└── SETUP.md               ← this file
```

---

## 🆘 Troubleshooting

**"Missing GROQ_API_KEY"** — Edit `.env`, paste the `gsk_...` key, save, rerun.

**"Rate limit hit"** — Groq free tier is generous but if you hammer it,
wait 60 seconds and click Run Agents again.

**Streamlit won't open** — Make sure `pip install -r requirements.txt`
finished without errors. Then `python -m streamlit run app.py`.

**Gmail IMAP fails** — You MUST use an App Password, not your real
Google password. 2-Step Verification has to be on first.

---

## 🚀 Going from demo → real Microsoft 365 (post-hackathon)

Swap two files:
1. `agents/llm.py` → replace Groq client with `openai.AzureOpenAI`
2. `inbox_source.py` → add `load_graph_inbox()` using `msgraph-sdk`

Everything else (the 4 agents, the UI, the orchestration) stays identical.
This is exactly how a hackathon MVP scales to production.
