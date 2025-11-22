import streamlit as st
import requests

API_URL = "http://localhost:8000/api"

st.title("MACIS – Adjuster Console (Stage 1)")

uploaded = st.file_uploader("Upload a document:")

if uploaded:
    files = {"file": (uploaded.name, uploaded.getvalue())}
    resp = requests.post(f"{API_URL}/ingest", files=files)
    st.json(resp.json())
