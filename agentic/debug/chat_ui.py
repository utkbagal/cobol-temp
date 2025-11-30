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
if "uploaded_file1" not in st.session_state:
    st.session_state.uploaded_file1 = None
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
    payload = {
        "message": user_text,
        "filename": st.session_state.uploaded_file.name,
        "correlation_id": st.session_state.correlation_id
        }

    intent_resp = requests.post(f"{API_BASE}/api/intent", json=payload)
    intent = intent_resp.json()
    #st.write(intent["intent"])
    if intent["intent"] == 'file_claim' or "file a claim" in user_text.lower():
        try:
            with st.spinner("Running claim pipeline..."):
                claim_process_resp = requests.post(f"{API_BASE}/api/claims/process", json=payload)
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ Error connecting to backend: {e}"
            })
            return

        if claim_process_resp.status_code == 200:
            result = claim_process_resp.json()
            #st.write(result)
            summary = result.get("context", {}).get("summary", "No summary available.")

            st.session_state.messages.append({
                "role": "assistant",
                "content": f"✅ **Claim Processed Successfully**\n\n### Summary:\n{summary} "
            })

            # Include agent traces
            for step in result.get("steps", []):
                formatted = json.dumps(step.get("output"), indent=2)
                agent_output = json.loads(formatted)
                agent_output = agent_output.get("agent_output")
                if isinstance(agent_output, dict):
                    agent_output = json.loads(agent_output)
                    formatted_output = "\n".join([f"{key} : {value}" for key, value in agent_output.items()])
                elif isinstance(agent_output, str):
                    formatted_output = agent_output

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": (f"**{step.get('agent')} Output:**\n```\n{formatted_output}\n```")
                })

        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ Claim processing failed:\n{claim_process_resp.text}"
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
            qna_resp = requests.post(f"{API_BASE}/api/claims/qna", json=payload)
    except Exception as e:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"❌ Error connecting to backend: {e}"
        })
        return

    if qna_resp.status_code == 200:
        result = qna_resp.json()
        #st.write(result)
        qna = result.get("context", {}).get("qna_result", {})
        answer = qna.get("answer")
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
            "content": f"❌ QnA failed:\n{qna_resp.text}"
        })


# ---------------------------------------------------------------------
# SIDEBAR WITH LOGIN + FILE UPLOAD
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("MACIS Assistant")

    username = st.text_input("Enter your name", value=st.session_state.username)
    st.session_state.username = username

    st.write(f"**Logged in as:** {st.session_state.username}")

    st.subheader("Upload Policy Document")
    uploaded1 = st.file_uploader("PDF / DOCX / TXT", type=["pdf", "docx", "txt"],key="pol")

    if uploaded1 and st.session_state.uploaded_file1 is None:
        st.session_state.uploaded_file1 = uploaded1
        files = {"file": (uploaded1.name, uploaded1.getvalue())}

        with st.spinner("Uploading & processing document..."):
            r = requests.post(f"{API_BASE}/api/pol_ingest", files=files)

        if r.status_code == 200:
            data = r.json()

            # API returned structure: {"correlation_id": {"correlation_id": "..."}}
            if isinstance(data.get("correlation_id"), dict):
                cid = data["correlation_id"]["correlation_id"]
            else:
                cid = data["correlation_id"]

            st.session_state.correlation_id = cid

    st.subheader("Upload Claim Document")
    uploaded = st.file_uploader("PDF / DOCX / TXT", type=["pdf", "docx", "txt"],key="clm")

    if uploaded and st.session_state.uploaded_file is None:
        st.session_state.uploaded_file = uploaded
        files = {"file": (uploaded.name, uploaded.getvalue())}

        with st.spinner("Uploading & processing document..."):
            payload = {
                'payload': json.dumps({'cid': st.session_state.correlation_id})
            }
            # Use the 'data' parameter for non-file form fields, passing the payload as a JSON string
            r = requests.post(f"{API_BASE}/api/claim_ingest", files=files, data=payload)


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