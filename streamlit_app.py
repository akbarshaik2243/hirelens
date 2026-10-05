"""HireLens — an interactive AI agent that answers recruiter questions about a candidate's profile.

Streamlit version (free hosting on Streamlit Community Cloud).
Agentic loop: question -> TOOL CALL search_profile(question) -> LLM answers from retrieved facts.

Secrets needed (Streamlit Cloud: App settings -> Secrets):
  HF_TOKEN = "<free Hugging Face read token>"
"""

import os
import re

import streamlit as st
from huggingface_hub import InferenceClient

from knowledge import PROFILE, FACTS

MODEL = os.environ.get("HF_MODEL", "Qwen/Qwen2.5-72B-Instruct")


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
- Never mention visas, sponsorship, contract types, or work arrangements. If asked about any of
  these, say "Please contact Akbar directly to discuss." and move on.
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


def answer(question):
    """Run the agent: retrieve facts, then have the LLM answer from them."""
    token = get_token()
    hits = search_profile(question)
    trace_steps = [
        ("Question received", question),
        ("Tool call: search_profile()",
         "\n".join(f"retrieved profile[{s}]" for s, _ in hits) or "(no matching facts)"),
    ]
    if not token:
        reply = ("The demo brain isn't connected yet: this app needs a free Hugging Face "
                 "token (HF_TOKEN secret) for the inference API. Meanwhile, reach Akbar at "
                 "akbarshaik2243@gmail.com.")
        trace_steps.append(("LLM step", "skipped — no HF_TOKEN configured"))
        return reply, trace_steps
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
        trace_steps.append(("LLM answer", f"{MODEL} composed the answer from {len(hits)} retrieved facts"))
    except Exception as e:
        reply = (f"The inference API returned an error ({type(e).__name__}). "
                 f"Please try again, or reach Akbar at akbarshaik2243@gmail.com.")
        trace_steps.append(("LLM step", f"failed: {type(e).__name__}"))
    return reply, trace_steps


# ---------------------------------------------------------------- UI content

SKILL_GROUPS = {
    "Agentic AI": ["MCP / FastMCP", "LangChain", "LangGraph", "Tool calling",
                   "Multi-agent orchestration", "ReAct patterns", "AWS Bedrock AgentCore",
                   "Google ADK", "Claude API"],
    "LLMs & GenAI": ["GPT-4 family", "Mistral-7B", "Llama / Qwen", "LoRA / PEFT",
                      "DPO", "Prompt engineering", "RAGAS eval", "PII masking"],
    "RAG & Retrieval": ["Hybrid search", "GraphRAG", "FAISS", "Pinecone / Qdrant",
                        "Milvus", "Weaviate", "Neo4j", "Elasticsearch"],
    "Serving & MLOps": ["vLLM", "Triton", "KServe", "MLflow", "Kubeflow",
                        "Airflow", "Kafka", "Drift detection"],
    "Cloud-Native": ["Kubernetes", "Helm", "Istio", "Docker", "Terraform",
                     "Argo CD", "AWS", "Azure", "GCP"],
    "Eval & Safety": ["DeepEval", "Promptfoo", "LLM-as-judge", "Red-teaming",
                      "OWASP LLM Top 10", "NeMo Guardrails", "Llama Guard"],
}

EXPERIENCE = [
    ("Applied Machine Learning Engineer", "Hewlett Packard Enterprise · Texas",
     "Apr 2026 – Present",
     "Built an MCP server with ~30 tools letting LLM agents manage ML pipelines on Kubernetes. "
     "Co-designed a shared Python MCP framework adopted across teams. Built DeepEval/Promptfoo "
     "eval harnesses, OWASP LLM Top-10 safety practices, and an end-to-end RAG pipeline on Mistral-7B."),
    ("Applied AI Engineer", "Teledyne Technologies Inc.",
     "Jan 2024 – Apr 2026",
     "RAG assistant (LangChain, FAISS, GPT-4): automated 60% of Tier-1 queries at 90%+ accuracy, "
     "42% faster responses. LoRA/PEFT fine-tuning, GraphRAG on Neo4j, DPO alignment, "
     "TensorRT-LLM/SGLang inference optimization."),
    ("MLOps Engineer / ML Platform Engineer", "Creative Newtech Ltd · India",
     "Feb 2020 – Aug 2022",
     "MLflow pipelines with full lineage, GitHub Actions CI/CD, drift detection (KS/PSI), "
     "SHAP/LIME explainability. Cut model failures 70%, API latency 28%. Passed 2 regulatory audits."),
]

QUESTION_CHIPS = {
    "Experience": ["What MCP work has Akbar done?",
                   "Tell me about his RAG experience",
                   "What did he build at HPE?"],
    "Skills": ["What are his strongest skills?",
               "Has he worked with Kubernetes and MLOps?",
               "What certifications does he have?"],
    "Availability": ["Is Akbar open to new opportunities?",
                     "How can I reach Akbar?",
                     "What is his contact info?"],
}

# ---------------------------------------------------------------- App

st.set_page_config(page_title="HireLens", page_icon=":robot_face:", layout="wide")

# Header
st.title("HireLens :robot_face:")
st.subheader("An AI agent that answers recruiter questions about a candidate's profile")
st.caption("Demo by **Akbar Shaik** — Applied AI/ML Engineer · Agentic AI, LLMs & RAG, MCP, MLOps on Kubernetes")

# Stat band
c1, c2, c3, c4 = st.columns(4)
c1.metric("Experience", "5+ years")
c2.metric("Skill areas", f"{sum(len(v) for v in SKILL_GROUPS.values())}+")
c3.metric("Companies", "3")
c4.metric("Certifications", "3")

st.divider()

tab_chat, tab_skills, tab_exp, tab_how = st.tabs(
    ["Chat with the agent", "Skills", "Experience", "How it works"])

# ---------------- Chat tab
with tab_chat:
    col_chat, col_trace = st.columns([3, 2])

    if "history" not in st.session_state:
        st.session_state.history = []
    if "trace" not in st.session_state:
        st.session_state.trace = []
    if "pending_q" not in st.session_state:
        st.session_state.pending_q = None

    with col_chat:
        st.markdown("**Ask anything about Akbar's background, skills, or availability.** "
                    "The agent searches his profile, then answers from what it finds.")
        for group, questions in QUESTION_CHIPS.items():
            st.markdown(f"_{group}_")
            chip_cols = st.columns(len(questions))
            for i, q in enumerate(questions):
                if chip_cols[i].button(q, key=f"chip_{group}_{i}"):
                    st.session_state.pending_q = q

        for q, a in st.session_state.history:
            with st.chat_message("user"):
                st.write(q)
            with st.chat_message("assistant", avatar="🤖"):
                st.write(a)

        user_q = st.chat_input("Type your question here...")
        question = st.session_state.pending_q or user_q
        st.session_state.pending_q = None

        if question:
            with st.spinner("Agent is searching the profile..."):
                reply, trace = answer(question)
            st.session_state.history.append((question, reply))
            st.session_state.trace = trace
            st.rerun()

    with col_trace:
        st.markdown("### Agent trace")
        st.caption("Every step the agent took to answer your last question.")
        if not st.session_state.trace:
            st.info("Ask a question and watch the agent work here: retrieval first, then the answer.")
        else:
            for i, (title, detail) in enumerate(st.session_state.trace, 1):
                with st.expander(f"Step {i}: {title}", expanded=(i <= 2)):
                    st.write(detail)

# ---------------- Skills tab
with tab_skills:
    st.markdown("### Technical skills")
    st.caption("Grouped by domain. Click any group to expand.")
    for group, skills in SKILL_GROUPS.items():
        with st.expander(f"{group} ({len(skills)})", expanded=False):
            pill_cols = st.columns(3)
            for i, skill in enumerate(skills):
                pill_cols[i % 3].markdown(f":white_check_mark: {skill}")

# ---------------- Experience tab
with tab_exp:
    st.markdown("### Professional experience")
    for title, company, dates, desc in EXPERIENCE:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.caption(f"{company} · {dates}")
            st.write(desc)

# ---------------- How it works tab
with tab_how:
    st.markdown("### How HireLens works")
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown("#### 1. You ask")
        st.write("Type any question about the candidate — skills, projects, availability, contact info.")
    with s2:
        st.markdown("#### 2. Agent retrieves")
        st.write("A `search_profile()` tool call finds the most relevant facts in the candidate's "
                 "profile knowledge base. The trace panel shows exactly what was retrieved.")
    with s3:
        st.markdown("#### 3. LLM answers")
        st.write("A large language model composes the answer strictly from the retrieved facts — "
                 "no hallucinations, no invented experience.")
    st.divider()
    st.markdown("#### Why this matters for hiring teams")
    st.write("This is the same **retrieval-augmented agent pattern** companies use for documentation "
             "copilots, support bots, and knowledge assistants: grounded answers, observable tool calls, "
             "and evaluable outputs. Point it at any knowledge base — a company wiki, a product manual, "
             "a resume database — and it works the same way.")
    with st.expander("Tech stack"):
        st.write("- UI: Streamlit (this app)\n"
                 "- Agent loop: tool-call retrieval + LLM composition\n"
                 "- LLM: Qwen 2.5 72B via Hugging Face serverless inference\n"
                 "- Knowledge base: structured profile facts (swap in any documents)\n"
                 "- Hosting: Streamlit Community Cloud (free)")

# Sidebar: contact card
with st.sidebar:
    st.markdown("### Contact Akbar")
    st.write(":email: akbarshaik2243@gmail.com")
    st.write(":telephone_receiver: (469) 629-9816")
    st.write(":round_pushpin: Irving, Texas, USA")
    st.divider()
    st.markdown("### Availability")
    st.success("Open to new opportunities")
    st.caption("Contact Akbar directly to discuss fit")
    st.divider()
    st.caption("HireLens demo · Built by Akbar Shaik")
