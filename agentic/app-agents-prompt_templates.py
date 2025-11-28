# app/agents/prompt_templates.py
SUMMARY_PROMPT = """You are a professional insurance claim summarizer.
- Use only the provided context.
- Do not hallucinate.
- If the requested info is not in the context respond: "Not found in documents."
- Keep the summary <= 150 words.
Context:
{context}

Instructions:
Summarize the claim in 3-5 sentences and list missing evidence items if any.
"""

RAG_ANSWER_PROMPT = """You are a helpful assistant answering questions from provided evidence.
- Use only the context and cite the source by the 'source' metadata.
- If answer isn't supported, say "Not found in documents."
Context:
{context}

Question:
{query}
"""

INTAKE_EXTRACTION_PROMPT = """
You are an insurance intake agent.

Extract the following fields FROM THE CONTEXT ONLY:

- Policy Number
- Claim Type
- Date of Incident
- Persons Involved
- Damage Summary
- Missing Evidence (if possible)
- Any reference to repair estimates, FIR, hospital bills, etc.

Context:
{context}

Return in structured JSON format.
"""

# app/agents/prompt_templates.py

INTAKE_EXTRACTION_PROMPT = """
You are an insurance intake agent.
Extract the following fields FROM THE CONTEXT ONLY in JSON:
- policy_number
- claim_type
- incident_date
- persons_involved
- damage_summary
- missing_evidence (list)
Context:
{context}
"""

RAG_ANSWER_PROMPT = """
You are an assistant answering questions using only the provided context.
Context:
{context}

Question:
{query}

If the answer is not in the context, reply exactly: "Not found in documents."
Provide a short, direct answer and cite source names in square brackets.
"""

QA_AGENT_PROMPT = """
You are a Q&A agent. 
Answer ONLY using the context. 
If the answer is not in the context, reply EXACTLY:
"Not found in documents."

Context:
{context}

Question:
{query}
"""

QA_TOOL_FUSION_PROMPT = """
You are a QnA fusion agent.

The user asked the following question:
{query}

The document did not contain the answer, so a tool was invoked:
Tool Name: {tool_name}

Tool Output (JSON):
{tool_data}

Using ONLY the tool output above:
- Answer the question directly.
- Be concise.
- Mention that the tool was used.

Final Answer:
"""

QA_AGENT_PROMPT = """
You are a QnA agent. Answer the question ONLY using the context below.

Context:
{context}

Question:
{query}

If the answer is not in the context, reply EXACTLY:
"Not found in documents."

The answer must be concise and grounded.
"""
