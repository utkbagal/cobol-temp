##frontend/ui.py

import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://core:8000/api")

st.title("MACIS - Adjuster Console (Stage 1)")

uploaded = st.file_uploader("Upload claim document (PDF/TXT/DOCX)", type=["pdf","txt","docx"])
if uploaded:
    files = {"file": (uploaded.name, uploaded.getvalue())}
    resp = requests.post(f"{API_URL}/ingest", files=files)
    st.write(resp.json())
