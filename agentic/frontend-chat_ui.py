# frontend/chat_ui.py
import streamlit as st
import requests
import json
import os

API_BASE = os.getenv("API_BASE", "http://localhost:8001")

st.set_page_config(page_title="MACIS Chat", layout="wide")
st.title("MACIS – Claims Assistant (Chat)")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "correlation_id" not in st.session_state:
    st.session_state.correlation_id = None

# Simple "login" stub
with st.sidebar:
    st.header("User")
    username = st.text_input("Enter your name", value="Adjuster")
    if username:
        st.session_state.username = username

st.write("You are logged in as:", st.session_state.get("username", "Adjuster"))

# Show existing chat
for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        st.info(msg["content"])
    else:
        st.write(f"**You:** {msg['content']}")

# Upload panel
uploaded = st.file_uploader("Upload claim document (PDF/DOCX/TXT)", type=["pdf","docx","txt"])
if uploaded and st.session_state.uploaded_file is None:
    st.session_state.uploaded_file = uploaded
    files = {"file": (uploaded.name, uploaded.getvalue())}
    r = requests.post(f"{API_BASE}/api/ingest", files=files)
    if r.status_code == 200:
        data = r.json()
        st.session_state.correlation_id = data["correlation_id"]
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Document '{uploaded.name}' uploaded. Correlation id: {data['correlation_id']}\nWhat would you like to do next?\n- File a claim\n- Ask questions about the document\n- View extracted information"
        })
        st.experimental_rerun()
    else:
        st.error("Ingest failed: " + r.text)

# Chat input area
user_input = st.text_input("Type a message or command (e.g., 'file a claim' or ask a question):")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Branch for "file a claim"
    if "file a claim" in user_input.lower():
        payload = {"filename": st.session_state.uploaded_file.name, "correlation_id": st.session_state.correlation_id}
        r = requests.post(f"{API_BASE}/api/claims/process", json=payload)
        if r.status_code == 200:
            result = r.json()
            summary = result.get("context", {}).get("summary", "No summary available.")
            st.session_state.messages.append({"role": "assistant", "content": f"Claim processed. Summary:\n{summary}"})

            # Attach agent traces
            for step in result.get("steps", []):
                formatted = json.dumps(step.get("output"), indent=2)
                st.session_state.messages.append({"role": "assistant", "content": f"**{step.get('agent')}** output:\n{formatted}"})
        else:
            st.session_state.messages.append({"role": "assistant", "content": f"Error processing claim: {r.text}"})

    else:
        # Treat as doc QA via RAG
        payload = {
            "query": user_input,
            "filename": st.session_state.uploaded_file.name if st.session_state.uploaded_file else '',
            "correlation_id": st.session_state.correlation_id
        }
        r = requests.post(f"{API_BASE}/api/claims/qna", json=payload)
        qna = r.json()["context"]["qna_result"]
        answer = qna["answer"]

        evidence_list = "\n".join([
            f"- {h['metadata']['source']}, score={h['score']:.4f}"
            for h in qna["evidence"]
            ])

        st.session_state.messages.append({
            "role": "assistant",
            "content": f"{answer}\n\n**Evidence Used:**\n{evidence_list}"
            })

# also show agent trace
        for step in result["steps"]:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"**{step['agent']} Output:**\n```json\n{json.dumps(step['output'], indent=2)}\n```"
            })


        if r.status_code == 200:
            ans = r.json().get("answer", "")
            evidence = r.json().get("evidence", [])
            ev_str = "\n".join([f"- {e['metadata'].get('source','?')} (score:{e['score']:.4f})" for e in evidence])
            st.session_state.messages.append({"role": "assistant", "content": f"Answer:\n{ans}\n\nEvidence:\n{ev_str}"})
        else:
            st.session_state.messages.append({"role": "assistant", "content": f"RAG QA failed: {r.text}"})

    st.experimental_rerun()
