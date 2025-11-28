# frontend/chat_ui.py
import streamlit as st
import requests
import json
import os

API_BASE = os.getenv("API_BASE", "http://localhost:8001")

st.set_page_config(page_title="MACIS Chat", layout="wide")

# -----------------------------------------------------------------------------------------
# SESSION STATE INIT
# -----------------------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "correlation_id" not in st.session_state:
    st.session_state.correlation_id = None
if "username" not in st.session_state:
    st.session_state.username = "Adjuster"

# -----------------------------------------------------------------------------------------
# SIDEBAR — USER + FILE UPLOAD
# -----------------------------------------------------------------------------------------
with st.sidebar:
    st.header("MACIS Assistant")
    
    # Login
    st.subheader("User Login")
    username = st.text_input("Enter your name", value=st.session_state.username)
    st.session_state.username = username

    st.write(f"**Logged in as:** {st.session_state.username}")

    # Upload
    st.subheader("Upload Claim Document")
    uploaded = st.file_uploader("PDF / DOCX / TXT", type=["pdf", "docx", "txt"])

    if uploaded and st.session_state.uploaded_file is None:
        st.session_state.uploaded_file = uploaded
        files = {"file": (uploaded.name, uploaded.getvalue())}

        with st.spinner("Uploading & processing document..."):
            r = requests.post(f"{API_BASE}/api/ingest", files=files)

        if r.status_code == 200:
            data = r.json()
            st.session_state.correlation_id = data["correlation_id"]

            st.session_state.messages.append({
                "role": "assistant",
                "content": (
                    f"📄 **Document uploaded:** {uploaded.name}\n"
                    f"🧵 **Correlation ID:** {data['correlation_id']}\n\n"
                    "What would you like to do next?\n"
                    "- File a claim\n"
                    "- Ask a question about the document\n"
                    "- View extracted information"
                )
            })
            st.experimental_rerun()
        else:
            st.error("❌ Document ingestion failed!\n" + r.text)


# -----------------------------------------------------------------------------------------
# MAIN CHAT WINDOW
# -----------------------------------------------------------------------------------------
st.title("MACIS – Claims Assistant (Chat Interface)")

chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            st.info(msg["content"])
        else:
            st.write(f"**You:** {msg['content']}")


# -----------------------------------------------------------------------------------------
# CHAT INPUT BOX
# -----------------------------------------------------------------------------------------
user_input = st.text_input("Type your message...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Ensure document is uploaded before processing claim or QnA
    if not st.session_state.uploaded_file:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "❗ Please upload a document before asking questions or filing a claim."
        })
        st.experimental_rerun()

    # -------------------------------------------------------------------------------------
    # 1️⃣ FILE A CLAIM
    # -------------------------------------------------------------------------------------
    if "file a claim" in user_input.lower():
        payload = {
            "filename": st.session_state.uploaded_file.name,
            "correlation_id": st.session_state.correlation_id
        }

        with st.spinner("Running claim pipeline..."):
            r = requests.post(f"{API_BASE}/api/claims/process", json=payload)

        if r.status_code == 200:
            result = r.json()
            summary = result.get("context", {}).get("summary", "No summary available.")

            st.session_state.messages.append({
                "role": "assistant",
                "content": f"✅ **Claim Processed Successfully**\n\n### Summary:\n{summary}"
            })

            # Agent traces
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

    # -------------------------------------------------------------------------------------
    # 2️⃣ QnA MODE (RAG / Semantic Search)
    # -------------------------------------------------------------------------------------
    else:
        payload = {
            "query": user_input,
            "filename": st.session_state.uploaded_file.name,
            "correlation_id": st.session_state.correlation_id
        }

        with st.spinner("Retrieving answer..."):
            r = requests.post(f"{API_BASE}/api/claims/qna", json=payload)

        if r.status_code == 200:
            result = r.json()

            # QnA result is inside orchestrator context
            qna = result.get("context", {}).get("qna_result", {})
            answer = qna.get("answer", "No answer received.")
            evidence = qna.get("evidence", [])

            evidence_list = "\n".join([
                f"- {h['metadata'].get('source','?')} (score={h['score']:.4f})"
                for h in evidence
            ]) or "No evidence returned."

            st.session_state.messages.append({
                "role": "assistant",
                "content": f"**Answer:**\n{answer}\n\n**Evidence Used:**\n{evidence_list}"
            })

            # Agent traces
            for step in result.get("steps", []):
                formatted = json.dumps(step.get("output"), indent=2)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"**{step.get('agent')} Output:**\n```json\n{formatted}\n```"
                })

        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ QnA Failed:\n{r.text}"
            })

    st.experimental_rerun()
