"""HireLens — an AI agent that answers recruiter questions about a candidate's profile.

Streamlit version (for free hosting on Streamlit Community Cloud).
Same agentic loop as the Gradio build:
  1. question in -> 2. TOOL CALL search_profile(question) -> 3. LLM answers from retrieved facts.

Secrets needed (Streamlit Cloud: App settings -> Secrets):
  HF_TOKEN = "<free Hugging Face read token>"
"""

import os
import re

import streamlit as st
from huggingface_hub import InferenceClient

from knowledge import PROFILE, FACTS

MODEL = os.environ.get("HF_MODEL", "meta-llama/Llama-3.3-70B-Instruct")


def get_token():
    try:
        return st.secrets["HF_TOKEN"]
    except Exception:
        return os.environ.get("HF_TOKEN")


STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "what", "whats", "which",
    "who", "whom", "how", "does", "do", "did", "has", "have", "had", "can",
    "could", "would", "should", "will", "with", "about", "tell", "me", "your",
    "you", "his", "him", "her", "its", "of", "in", "on", "for", "to", "and",
    "or", "akbar", "shaik", "he", "she", "it", "at", "by", "from", "as",
}

SYSTEM_PROMPT = """You are "HireLens", the AI representative of Akbar Shaik, an Applied AI/ML Engineer.
A recruiter or hiring manager is asking about Akbar. Answer helpfully and concisely (2-5 sentences
unless they ask for detail), as his representative ("Akbar has...", "He built...").

Rules:
- Use ONLY the profile excerpts provided. Do not invent experience, skills, or facts.
- If the excerpts don't cover the question, say so honestly and suggest contacting Akbar directly.
- Keep answers factual and professional. Mention metrics when relevant.
- Contact: akbarshaik2243@gmail.com, (469) 629-9816, Irving, Texas.
- Availability: remote CONTRACT roles (C2C through his own employer). H-1B, no sponsorship needed.
"""


def search_profile(query: str, top_k: int = 4):
    """TOOL: keyword search over the profile facts. Returns (section, text) hits."""
    tokens = [t for t in re.findall(r"[a-z0-9+/#.]+", query.lower()) if t not in STOPWORDS]
    scored = []
    for section, text in FACTS:
        low = text.lower()
        score = sum(2 for tok in tokens if tok in low)
        if len(tokens) > 1 and " ".join(tokens) in low:
            score += 3
        if score > 0:
            scored.append((score, section, text))
    scored.sort(key=lambda x: -x[0])
    return [(s, t) for _, s, t in scored[:top_k]]


def format_trace(question, hits):
    lines = [f"question: {question}", "",
             f"tool_call: search_profile({question!r})"]
    if hits:
        lines += [f"  -> retrieved: profile[{s}]" for s, _ in hits]
    else:
        lines.append("  -> retrieved: (no matching facts)")
    lines += ["", f"llm: {MODEL} composing answer from retrieved facts..."]
    return "\n".join(lines)


def answer(question):
    token = get_token()
    if not token:
        return ("The demo brain isn't connected yet: this app needs a free Hugging Face "
                "token (HF_TOKEN secret) for the inference API. Meanwhile, reach Akbar at "
                "akbarshaik2243@gmail.com."), "trace: skipped (no HF_TOKEN configured)"
    hits = search_profile(question)
    trace = format_trace(question, hits)
    context = "\n\n".join(f"[{s}]\n{t}" for s, t in hits) or "(No directly matching profile facts found.)"
    client = InferenceClient(token=token)
    try:
        completion = client.chat_completion(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Profile excerpts:\n{context}\n\nQuestion: {question}"},
            ],
            max_tokens=400,
            temperature=0.3,
        )
        reply = completion.choices[0].message.content.strip()
    except Exception as e:
        reply = (f"The inference API returned an error ({type(e).__name__}). "
                 f"Please try again, or reach Akbar at akbarshaik2243@gmail.com.")
    return reply, trace


SUGGESTED = [
    "What MCP work has Akbar done?",
    "Tell me about his RAG experience",
    "Is Akbar open to contract roles?",
    "What is his contact info?",
]

st.set_page_config(page_title="HireLens", page_icon="\U0001F916", layout="wide")
st.title("HireLens \U0001F916")
st.caption("An AI agent that answers questions about a candidate's profile — "
           "demo by Akbar Shaik, Applied AI/ML Engineer (Agentic AI, LLMs & RAG, MCP, MLOps). "
           "It searches his profile, then answers from what it finds.")

if "history" not in st.session_state:
    st.session_state.history = []
if "trace" not in st.session_state:
    st.session_state.trace = "Ask a question to see the agent's tool calls here."
if "pending_q" not in st.session_state:
    st.session_state.pending_q = None

col_chat, col_trace = st.columns([3, 2])

with col_chat:
    for q, a in st.session_state.history:
        with st.chat_message("user"):
            st.write(q)
        with st.chat_message("assistant"):
            st.write(a)

    st.write("Try:")
    sq_cols = st.columns(len(SUGGESTED))
    for i, q in enumerate(SUGGESTED):
        if sq_cols[i].button(q, key=f"sq_{i}"):
            st.session_state.pending_q = q

    user_q = st.chat_input("Ask about Akbar's background, skills, or availability")
    question = st.session_state.pending_q or user_q
    st.session_state.pending_q = None

    if question:
        with st.spinner("Agent is searching the profile..."):
            reply, trace = answer(question)
        st.session_state.history.append((question, reply))
        st.session_state.trace = trace
        st.rerun()

with col_trace:
    st.subheader("Agent trace")
    st.code(st.session_state.trace, language="text")

st.divider()
st.caption("HireLens demo by Akbar Shaik · Answers only from his public profile · "
           "Recruiters: akbarshaik2243@gmail.com · (469) 629-9816")
