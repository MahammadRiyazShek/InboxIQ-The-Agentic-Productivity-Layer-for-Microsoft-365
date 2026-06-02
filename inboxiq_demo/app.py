"""
InboxIQ — The Agentic Productivity Layer for Microsoft 365
Streamlit demo app. Run with:  streamlit run app.py
"""
import streamlit as st
from concurrent.futures import ThreadPoolExecutor
import time
from agents import classify, summarize, draft, schedule
from inbox_source import load_demo_inbox, load_gmail_inbox

# ─────────────────────────── PAGE CONFIG & STYLE ───────────────────────────
st.set_page_config(
    page_title="InboxIQ — AI Workplace Assistant",
    page_icon="📬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.main { background: #fafbfd; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
.email-card {
    background: white; border: 1px solid #e6e8ec; border-radius: 12px;
    padding: 16px; margin-bottom: 12px; transition: all .15s ease;
}
.email-card:hover { border-color: #4f46e5; box-shadow: 0 4px 12px rgba(79,70,229,.08); }
.badge {
    display: inline-block; padding: 3px 10px; border-radius: 999px;
    font-size: 11px; font-weight: 600; letter-spacing: .3px;
}
.b-urgent  { background:#fee2e2; color:#b91c1c; }
.b-action  { background:#fef3c7; color:#a16207; }
.b-fyi     { background:#dbeafe; color:#1e40af; }
.b-noise   { background:#f3f4f6; color:#6b7280; }
.brief-card {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: white; padding: 18px; border-radius: 14px; margin-bottom: 14px;
}
.brief-stat { font-size: 28px; font-weight: 700; line-height: 1; }
.brief-label { font-size: 12px; opacity: .9; }
.reply-card {
    background: #f8fafc; border-left: 3px solid #4f46e5;
    padding: 12px 14px; border-radius: 6px; margin: 8px 0;
    font-size: 14px;
}
h1, h2, h3 { color: #1e293b; }
.small-muted { color:#64748b; font-size: 12px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────── SESSION STATE ───────────────────────────
if "emails" not in st.session_state:
    st.session_state.emails = []
if "results" not in st.session_state:
    st.session_state.results = {}  # email_id -> {label, summary, draft, schedule}
if "selected_id" not in st.session_state:
    st.session_state.selected_id = None
if "sent_ids" not in st.session_state:
    st.session_state.sent_ids = set()


# ─────────────────────────── SIDEBAR ───────────────────────────
with st.sidebar:
    st.markdown("### 📬 **InboxIQ**")
    st.caption("AI Assistant for Work")
    st.markdown("---")

    user = st.text_input("Logged in as", value="Alex Chen", disabled=True)
    st.caption("Director of Product · Acme Corp")
    st.markdown("---")

    source = st.radio(
        "Inbox source",
        ["Demo data (10 sample emails)", "Live Gmail (IMAP)"],
        index=0,
    )

    if st.button("📥 Load Inbox", use_container_width=True, type="primary"):
        with st.spinner("Fetching emails..."):
            try:
                if source.startswith("Demo"):
                    st.session_state.emails = load_demo_inbox()
                else:
                    st.session_state.emails = load_gmail_inbox(limit=10)
                st.session_state.results = {}
                st.session_state.selected_id = None
                st.success(f"Loaded {len(st.session_state.emails)} emails")
            except Exception as e:
                st.error(str(e))

    if st.button("🤖 Run Agents on Inbox", use_container_width=True,
                 disabled=not st.session_state.emails):
        run_agents_on_all()  # defined below

    st.markdown("---")
    st.caption("Powered by Llama 3.3 70B via Groq")
    st.caption("Production: Azure OpenAI GPT-4o + MS Graph")


# ─────────────────────────── AGENT ORCHESTRATION ───────────────────────────
def process_one(email):
    """Run all 4 agents on one email. Parallel calls inside."""
    with ThreadPoolExecutor(max_workers=4) as ex:
        f_cls = ex.submit(classify, email)
        f_sum = ex.submit(summarize, email)
        f_drf = ex.submit(draft, email)
        f_sch = ex.submit(schedule, email)
        return {
            "classification": f_cls.result(),
            "summary": f_sum.result(),
            "draft": f_drf.result(),
            "schedule": f_sch.result(),
        }


def run_agents_on_all():
    progress = st.progress(0, text="Agents starting…")
    total = len(st.session_state.emails)
    for i, em in enumerate(st.session_state.emails):
        if em["id"] in st.session_state.results:
            progress.progress((i + 1) / total)
            continue
        try:
            st.session_state.results[em["id"]] = process_one(em)
        except Exception as e:
            st.session_state.results[em["id"]] = {
                "classification": {"label": "FYI", "priority_score": 1,
                                   "reason": f"error: {e}", "mentions_user": False},
                "summary": "(agent error)",
                "draft": {"concise": "", "detailed": "", "decline_or_defer": ""},
                "schedule": {"is_meeting_request": False, "proposed_slots": []},
            }
        progress.progress((i + 1) / total,
                          text=f"Processed {i+1}/{total}: {em['subject'][:40]}…")
    progress.empty()
    st.success(f"✅ All {total} emails processed by 4 agents in parallel")


# ─────────────────────────── HEADER ───────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("## Good morning, Alex 👋")
    st.caption("Here's your AI-generated briefing for Tuesday, June 2, 2026")
with col_h2:
    st.markdown(f"<div style='text-align:right; padding-top:18px;'>"
                f"<span class='small-muted'>🕒 9:41 AM IST</span></div>",
                unsafe_allow_html=True)


# ─────────────────────────── DAILY BRIEFING CARDS ───────────────────────────
if st.session_state.emails and st.session_state.results:
    res = st.session_state.results
    labels = [res[e["id"]]["classification"]["label"]
              for e in st.session_state.emails if e["id"] in res]
    n_urgent = sum(1 for l in labels if l == "URGENT")
    n_action = sum(1 for l in labels if l == "ACTION")
    n_fyi    = sum(1 for l in labels if l == "FYI")
    n_noise  = sum(1 for l in labels if l == "NOISE")
    meetings = sum(1 for e in st.session_state.emails
                   if e["id"] in res and res[e["id"]]["schedule"]["is_meeting_request"])

    b1, b2, b3, b4, b5 = st.columns(5)
    for col, n, lbl, emoji in [
        (b1, n_urgent, "Urgent", "🔴"),
        (b2, n_action, "Action Needed", "🟡"),
        (b3, n_fyi,    "FYI", "🔵"),
        (b4, n_noise,  "Auto-archived", "⚪"),
        (b5, meetings, "Meeting Requests", "📅"),
    ]:
        with col:
            st.markdown(
                f"<div class='brief-card'>"
                f"<div class='brief-label'>{emoji} {lbl}</div>"
                f"<div class='brief-stat'>{n}</div>"
                f"</div>", unsafe_allow_html=True)

    minutes_saved = n_urgent * 8 + n_action * 5 + n_fyi * 2 + n_noise * 1
    st.info(f"⏱️ **Estimated time saved this morning: {minutes_saved} minutes** "
            f"({minutes_saved/60:.1f} hours/week if sustained)")

    st.markdown("---")


# ─────────────────────────── TWO-COLUMN INBOX + DETAIL ───────────────────────────
left, right = st.columns([1.1, 1.4])

with left:
    st.markdown("### 📥 Inbox")
    if not st.session_state.emails:
        st.info("👈 Click **Load Inbox** then **Run Agents** in the sidebar to start.")
    else:
        # Sort: urgent first, then by priority score
        def sort_key(e):
            r = st.session_state.results.get(e["id"])
            if not r: return (99, 0)
            label_order = {"URGENT": 0, "ACTION": 1, "FYI": 2, "NOISE": 3}
            return (label_order.get(r["classification"]["label"], 4),
                    -r["classification"]["priority_score"])
        sorted_emails = sorted(st.session_state.emails, key=sort_key)

        for em in sorted_emails:
            r = st.session_state.results.get(em["id"])
            label = r["classification"]["label"] if r else "—"
            badge_cls = {"URGENT":"b-urgent","ACTION":"b-action",
                         "FYI":"b-fyi","NOISE":"b-noise"}.get(label, "b-fyi")
            sent_mark = " ✅ Replied" if em["id"] in st.session_state.sent_ids else ""

            with st.container():
                st.markdown(
                    f"<div class='email-card'>"
                    f"<div style='display:flex; justify-content:space-between;'>"
                    f"<b>{em['from_name']}</b>"
                    f"<span class='badge {badge_cls}'>{label}</span>"
                    f"</div>"
                    f"<div style='margin-top:4px; font-size:14px;'>{em['subject']}</div>"
                    f"<div class='small-muted' style='margin-top:6px;'>"
                    f"{em['received']}{sent_mark}</div>"
                    f"</div>", unsafe_allow_html=True)
                if st.button(f"Open →", key=f"open_{em['id']}"):
                    st.session_state.selected_id = em["id"]

with right:
    st.markdown("### 🤖 AI Workspace")
    sid = st.session_state.selected_id
    if not sid:
        st.info("Select an email on the left to see the AI's analysis and drafts.")
    else:
        em = next(e for e in st.session_state.emails if e["id"] == sid)
        r  = st.session_state.results.get(sid)

        st.markdown(f"**From:** {em['from_name']} `<{em['from_email']}>`")
        st.markdown(f"**Subject:** {em['subject']}")
        with st.expander("📄 Full email body", expanded=False):
            st.text(em["body"])

        if not r:
            st.warning("Agents have not processed this email yet.")
        else:
            cls = r["classification"]
            color = {"URGENT":"🔴","ACTION":"🟡","FYI":"🔵","NOISE":"⚪"}.get(cls["label"],"⚪")
            st.markdown(f"#### {color} {cls['label']} · priority {cls['priority_score']}/10")
            st.caption(f"_Reason:_ {cls['reason']}")

            st.markdown("##### 🧠 One-sentence summary")
            st.success(r["summary"])

            if r["schedule"]["is_meeting_request"]:
                st.markdown("##### 📅 Scheduler Agent detected a meeting")
                st.write(f"**Title:** {r['schedule']['title']}")
                st.write(f"**Duration:** {r['schedule']['duration_min']} min")
                st.write("**Proposed slots:**")
                for s in r["schedule"]["proposed_slots"]:
                    st.write(f"- {s}")
                if st.button("📨 Send slot proposals", key=f"sch_{sid}"):
                    st.session_state.sent_ids.add(sid)
                    st.success("Slot proposals sent (simulated)")

            st.markdown("##### ✍️ Drafted replies (RAG over your prior threads)")
            d = r["draft"]
            for variant, emoji, title in [
                ("concise", "⚡", "Concise"),
                ("detailed", "📝", "Detailed"),
                ("decline_or_defer", "🛑", "Decline / Defer"),
            ]:
                text = d.get(variant, "")
                if not text: continue
                st.markdown(f"**{emoji} {title}**")
                st.markdown(f"<div class='reply-card'>{text}</div>",
                            unsafe_allow_html=True)
                c1, c2 = st.columns([1, 4])
                with c1:
                    if st.button("Send", key=f"send_{sid}_{variant}"):
                        st.session_state.sent_ids.add(sid)
                        st.toast(f"✅ Reply sent ({title})", icon="📨")
