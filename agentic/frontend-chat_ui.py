import streamlit as st
import requests

API_BASE = "http://localhost:8001"

st.set_page_config(page_title="MACIS Chat", layout="wide")
st.title("MACIS – Claims Assistant")

# -------------------------
# Session state
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "correlation_id" not in st.session_state:
    st.session_state.correlation_id = None
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

# -------------------------
# Chat display
# -------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -------------------------
# Upload document
# -------------------------
uploaded = st.file_uploader("Upload Claim Document:", type=["txt","pdf","docx"])

if uploaded and st.session_state.uploaded_file is None:
    st.session_state.uploaded_file = uploaded

    files = {"file": (uploaded.name, uploaded.getvalue())}
    r = requests.post(f"{API_BASE}/api/ingest", files=files)
    data = r.json()

    st.session_state.correlation_id = data["correlation_id"]

    st.session_state.messages.append({
        "role": "assistant",
        "content": f"Document '{uploaded.name}' received. What would you like to do next?\n\n- File a claim\n- Ask questions about the document\n- View extracted information"
    })
    st.rerun()

# -------------------------
# User input (chat)
# -------------------------
user_input = st.chat_input("Ask MACIS...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Branching logic
    if "file a claim" in user_input.lower():
        payload = {
            "filename": st.session_state.uploaded_file.name,
            "correlation_id": st.session_state.correlation_id
        }
        r = requests.post(f"{API_BASE}/api/claims/process", json=payload)
        result = r.json()

        summary = result["context"].get("summary", "No summary")

        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Claim filed.\n\n**Summary:**\n{summary}\n\n**Agent steps:**"
        })

        # Show agent trace
        for step in result["steps"]:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"**{step['agent']} Output:**\n```json\n{step['output']}\n```"
            })

    else:
        # Ask RAG QA
        data = {"query": user_input}
        r = requests.post(f"{API_BASE}/api/rag-answer", data=data)
        ans = r.json()["answer"]

        st.session_state.messages.append({"role": "assistant", "content": ans})

    st.rerun()
