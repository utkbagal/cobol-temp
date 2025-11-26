# frontend/ui.py
import streamlit as st
import requests
import time

API_BASE = st.secrets.get("API_BASE", "http://localhost:8000")

st.set_page_config(page_title="MACIS Adjuster Console", layout="wide")
st.title("MACIS — Adjuster Console")

# Upload
with st.sidebar:
    st.header("Upload / Actions")
    uploaded = st.file_uploader("Upload claim doc", type=["pdf","docx","txt"])
    filename = st.text_input("Filename (for demo)", value="uploaded_claim.txt")
    if st.button("Ingest & Start Process"):
        if uploaded is None:
            st.warning("Upload a document first")
        else:
            files = {"file": (uploaded.name, uploaded.getvalue())}
            r = requests.post(f"{API_BASE}/api/ingest", files=files)
            if r.status_code == 200:
                res = r.json()
                st.success("Ingested. Starting processing...")
                cid = res.get("correlation_id")
                # call claims/process
                proc = requests.post(f"{API_BASE}/api/claims/process", json={"filename": uploaded.name, "correlation_id": cid})
                if proc.status_code == 200:
                    proc_json = proc.json()
                    st.session_state["last_result"] = proc_json
                    st.experimental_rerun()
                else:
                    st.error(proc.text)

    if st.button("Re-run Risk Triage"):
        result = st.session_state.get("last_result")
        if not result:
            st.warning("No previous run found")
        else:
            cid = result.get("correlation_id")
            resp = requests.post(f"{API_BASE}/api/claims/rerun_triage", json={"correlation_id": cid})
            st.write(resp.json())

    if st.button("Send Notification (mock)"):
        result = st.session_state.get("last_result")
        if result:
            cid = result.get("correlation_id")
            resp = requests.post(f"{API_BASE}/api/tools/notify", json={"correlation_id": cid, "message": "Please provide incident photos"})
            st.write(resp.json())

# Main panel: timeline and details
st.header("Latest Claim Run")
last = st.session_state.get("last_result")
if not last:
    st.info("No runs yet. Upload a document and click 'Ingest & Start Process'")
else:
    st.subheader(f"Correlation ID: {last.get('correlation_id')}")
    context = last.get("context", {})
    st.markdown("**Extracted Context**")
    st.json(context)

    st.markdown("**Agent Timeline**")
    steps = last.get("steps", [])
    for i, step in enumerate(steps):
        with st.expander(f"{i+1}. {step.get('agent')}"):
            st.markdown("**Output**")
            st.json(step.get("output"))
            # If evidence provided
            if step.get("output", {}).get("evidence"):
                st.markdown("**Evidence**")
                for e in step["output"]["evidence"]:
                    st.write(e.get("text")[:400], "...")  # truncated preview
                    st.caption(f"source: {e.get('metadata', {}).get('source','unknown')}")
