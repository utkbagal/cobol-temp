# frontend/chat_ui.py
import streamlit as st
import requests
import json
import os

API_BASE = os.getenv("API_BASE", "http://localhost:8002")

st.set_page_config(page_title="MACIS Chat", layout="wide")

# ---------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "correlation_id" not in st.session_state:
    st.session_state.correlation_id = None
if "username" not in st.session_state:
    st.session_state.username = "Adjuster"
if "pending_input" not in st.session_state:
    st.session_state.pending_input = ""  # holds text typed by user

# ---------------------------------------------------------------------
# CALLBACK FUNCTION (RUNS ONLY WHEN USER PRESSES ENTER IN TEXTBOX)
# ---------------------------------------------------------------------
def handle_message():
    user_text = st.session_state.pending_input.strip()

    if not user_text:
        return  # ignore empty submissions

    # Add user message ONCE
    st.session_state.messages.append({"role": "user", "content": user_text})

    # Reset text field so it does not retrigger callback
    st.session_state.pending_input = ""

    # Require file upload before processing anything
    if not st.session_state.uploaded_file:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "❗ Please upload a document before asking questions or filing a claim."
        })
        return

    # -----------------------------------------------------------------
    # Handle claim filing
    # -----------------------------------------------------------------
    if "file a claim" in user_text.lower():
        payload = {
            "filename": st.session_state.uploaded_file.name,
            "correlation_id": st.session_state.correlation_id
        }

        try:
            with st.spinner("Running claim pipeline..."):
                r = requests.post(f"{API_BASE}/api/claims/process", json=payload)
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ Error connecting to backend: {e}"
            })
            return

        if r.status_code == 200:
            result = r.json()
            summary = result.get("context", {}).get("summary", "No summary available.")

            st.session_state.messages.append({
                "role": "assistant",
                "content": f"✅ **Claim Processed Successfully**\n\n### Summary:\n{summary}"
            })

            # Include agent traces
            for step in result.get("steps", []):
                formatted = json.dumps(step.get("output"), indent=2)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"**{step.get('agent')} Output:**\n```json\n{formatted}\n```"
                })

        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ Claim processing failed:\n{r.text}"
            })

        return

    # -----------------------------------------------------------------
    # Otherwise: Perform QnA
    # -----------------------------------------------------------------
    payload = {
        "query": user_text,
        "filename": st.session_state.uploaded_file.name,
        "correlation_id": st.session_state.correlation_id
    }

    try:
        with st.spinner("Retrieving answer..."):
            r = requests.post(f"{API_BASE}/api/claims/qna", json=payload)
    except Exception as e:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"❌ Error connecting to backend: {e}"
        })
        return

    if r.status_code == 200:
        result = r.json()
        qna = result.get("context", {}).get("qna_result", {})
        answer = qna.get("answer", "No answer returned.")
        evidence = qna.get("evidence", [])

        ev = "\n".join([
            f"- {h['metadata'].get('source','?')} (score={h.get('score',0):.4f})"
            for h in evidence
        ]) or "No evidence."

        st.session_state.messages.append({
            "role": "assistant",
            "content": f"**Answer:**\n{answer}\n\n**Evidence:**\n{ev}"
        })

        # Agent traces
        for step in result.get("steps", []):
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"**{step['agent']} Output:**\n```json\n{json.dumps(step['output'], indent=2)}\n```"
            })
    else:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"❌ QnA failed:\n{r.text}"
        })


# ---------------------------------------------------------------------
# SIDEBAR WITH LOGIN + FILE UPLOAD
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("MACIS Assistant")

    username = st.text_input("Enter your name", value=st.session_state.username)
    st.session_state.username = username

    st.write(f"**Logged in as:** {st.session_state.username}")

    st.subheader("Upload Claim Document")
    uploaded = st.file_uploader("PDF / DOCX / TXT", type=["pdf", "docx", "txt"])

    if uploaded and st.session_state.uploaded_file is None:
        st.session_state.uploaded_file = uploaded
        files = {"file": (uploaded.name, uploaded.getvalue())}

        with st.spinner("Uploading & processing document..."):
            r = requests.post(f"{API_BASE}/api/ingest", files=files)

        if r.status_code == 200:
            data = r.json()

            # API returned structure: {"correlation_id": {"correlation_id": "..."}}
            if isinstance(data.get("correlation_id"), dict):
                cid = data["correlation_id"]["correlation_id"]
            else:
                cid = data["correlation_id"]

            st.session_state.correlation_id = cid

            st.session_state.messages.append({
                "role": "assistant",
                "content": (
                    f"📄 **Document uploaded:** {uploaded.name}\n"
                    f"🧵 **Correlation ID:** {cid}\n\n"
                    "What would you like to do next?\n"
                    "- File a claim\n"
                    "- Ask a question about the document\n"
                    "- View extracted information"
                )
            })

        else:
            st.error("❌ Document ingestion failed!\n" + r.text)


# ---------------------------------------------------------------------
# MAIN CHAT WINDOW
# ---------------------------------------------------------------------
st.title("MACIS – Claims Assistant")

chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            st.info(msg["content"])
        else:
            st.write(f"**You:** {msg['content']}")


# ---------------------------------------------------------------------
# CHAT INPUT (WITH CALLBACK — NO LOOPS, NO DUPLICATES)
# ---------------------------------------------------------------------
st.text_input(
    "Type your message...",
    key="pending_input",
    on_change=handle_message     # <-- calls the handler ONCE
)
