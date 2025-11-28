# -----------------------------------------------------------------------------------------
# SAFE CHAT INPUT (NO LOOPING)
# -----------------------------------------------------------------------------------------
user_input = st.text_input("Type your message...", key="chat_input")

if user_input and st.session_state.chat_input != "":
    message_to_process = user_input.strip()

    # Immediately clear the text input to prevent loop
    st.session_state.chat_input = ""

    # Display the user's message only once
    st.session_state.messages.append({"role": "user", "content": message_to_process})

    # Require document before starting chat
    if not st.session_state.uploaded_file:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "❗ Please upload a document before asking questions or filing a claim."
        })
        st.stop()

    # -------------------------------------------------------------------------
    # Processing logic
    # -------------------------------------------------------------------------
    if "file a claim" in message_to_process.lower():
        payload = {
            "filename": st.session_state.uploaded_file.name,
            "correlation_id": st.session_state.correlation_id
        }
        with st.spinner("Running claim pipeline..."):
            r = requests.post(f"{API_BASE}/api/claims/process", json=payload)

        if r.status_code == 200:
            result = r.json()
            summary = result.get("context", {}).get("summary", "No summary.")
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"✅ Claim processed.\n\n**Summary:**\n{summary}"
            })

            for step in result.get("steps", []):
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"**{step['agent']} Output:**\n```json\n{json.dumps(step['output'], indent=2)}\n```"
                })

        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ Claim processing failed:\n{r.text}"
            })

    else:
        # QnA branch
        payload = {
            "query": message_to_process,
            "filename": st.session_state.uploaded_file.name,
            "correlation_id": st.session_state.correlation_id
        }

        with st.spinner("Retrieving answer..."):
            r = requests.post(f"{API_BASE}/api/claims/qna", json=payload)

        if r.status_code == 200:
            result = r.json()
            qna = result.get("context", {}).get("qna_result", {})
            answer = qna.get("answer")
            evidence = qna.get("evidence", [])

            ev = "\n".join([f"- {h['metadata'].get('source')} (score={h['score']:.4f})" for h in evidence])

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

    # STOP after handling input, do not rerun
    st.stop()
