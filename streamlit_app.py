"""HireLens — Akbar Shaik's personal website with an AI agent chat.

Sections: About, Experience, Skills, Projects, Chat with the agent, Schedule a call.
The agent answers recruiter questions from the profile knowledge base only:
never visas/sponsorship/contract terms, never personal questions.

Secrets (Streamlit Cloud -> App settings -> Secrets):
  HF_TOKEN = "<free Hugging Face read token>"
  CAL_LINK = "<public Cal.com booking link>"
"""

import os
import re

import streamlit as st
from huggingface_hub import InferenceClient

from knowledge import PROFILE, FACTS

MODEL = os.environ.get("HF_MODEL", "Qwen/Qwen2.5-72B-Instruct")


def get_secret(name):
    try:
        return st.secrets[name]
    except Exception:
        return os.environ.get(name)


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
- Write like a human colleague, not a bot: natural, conversational sentences, no stiff
  corporate filler, no bullet-point-everything. Vary your phrasing.
- Say each fact exactly once — never repeat a sentence, phrase, or paragraph.
- Contact: never write out Akbar's email address or phone number in your answers.
  If someone needs to reach him, direct them to book a 30-minute intro call at
  https://cal.com/akbar-shaik/intro-call (weekdays 2-4 PM America/Chicago, Google Meet link emailed automatically).
- Never mention visas, sponsorship, contract types, or work arrangements. If asked about any of
  these, say "Please contact Akbar directly to discuss." and move on.
- Never answer personal questions: age, date of birth, home address, family, marital status,
  salary or compensation, or anything not covered by the profile excerpts. If asked, say
  "I can't share personal details — the best way to reach Akbar is to book an intro call
  at https://cal.com/akbar-shaik/intro-call."
- Always shareable (never treat as personal): his full name (Akbar Shaik), job title,
  city (Irving, Texas), qualifications summary, and call availability. Never share his
  email address or phone number — direct people to the booking link instead.
- If the visitor wants to schedule a call, offer it directly: share the booking link
  https://cal.com/akbar-shaik/intro-call and mention 30-minute intro calls on weekdays
  2-4 PM America/Chicago, with a Google Meet link emailed automatically after booking.
"""


SYNONYMS = {
    "qualifications": ["experience", "skills", "education", "degree", "master", "certifications", "background"],
    "qualification": ["experience", "skills", "education", "degree", "master", "certifications", "background"],
    "background": ["experience", "education", "skills"],
    "timing": ["schedule", "availability", "call", "meet"],
    "timings": ["schedule", "availability", "call", "meet"],
    "meet": ["schedule", "availability", "call", "booking"],
    "meeting": ["schedule", "availability", "call", "booking"],
    "available": ["schedule", "availability", "call"],
    "availability": ["schedule", "call", "booking"],
    "name": ["akbar", "shaik", "identity"],
}


def search_profile(query: str, top_k: int = 4):
    """TOOL: keyword search over the profile facts. Returns (section, text) hits."""
    tokens = [t for t in re.findall(r"[a-z0-9+/#.]+", query.lower()) if t not in STOPWORDS]
    # Pronouns refer to Akbar — keep that link instead of dropping them silently.
    if re.search(r"\b(he|his|him)\b", query.lower()):
        tokens += ["akbar", "shaik"]
    expanded = list(tokens)
    for tok in tokens:
        expanded.extend(SYNONYMS.get(tok, []))
    tokens = expanded
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


def _scrub_contact(text):
    """Remove email addresses and phone numbers; point to scheduling instead."""
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "the booking link", text)
    text = re.sub(r"\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}", "the booking link", text)
    return text


def _dedupe(text):
    """Collapse exact repeated sentences/paragraphs the model sometimes emits twice."""
    import itertools
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    paras = [p for p, _ in itertools.groupby(paras)]
    out = []
    for p in paras:
        sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", p) if s.strip()]
        sents = [s for s, _ in itertools.groupby(sents)]
        out.append(" ".join(sents))
    return "\n\n".join(out)


def answer(question):
    """Run the agent: retrieve facts, then have the LLM answer from them."""
    token = get_secret("HF_TOKEN")
    hits = search_profile(question)
    trace_steps = [
        ("Question received", question),
        ("Tool call: search_profile()",
         "\n".join(f"retrieved profile[{s}]" for s, _ in hits) or "(no matching facts)"),
    ]
    if not token:
        reply = ("The demo brain isn't connected yet: this app needs a free Hugging Face "
                 "token (HF_TOKEN secret) for the inference API. Meanwhile, the best way to reach "
                 "Akbar is to book an intro call at https://cal.com/akbar-shaik/intro-call.")
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
        reply = _dedupe(reply)
        reply = _scrub_contact(reply)
        trace_steps.append(("LLM answer", f"{MODEL} composed the answer from {len(hits)} retrieved facts"))
    except Exception as e:
        reply = (f"The inference API returned an error ({type(e).__name__}). "
                 f"Please try again, or book an intro call at https://cal.com/akbar-shaik/intro-call.")
        trace_steps.append(("LLM step", f"failed: {type(e).__name__}"))
    return reply, trace_steps


# ---------------------------------------------------------------- Content

ABOUT = (
    "I'm an Applied Machine Learning Engineer with 5+ years of experience building scalable, "
    "production-grade ML systems, with a strong focus on LLMs, MLOps, and AI platform engineering. "
    "My recent work centers on the Model Context Protocol (MCP): I've built production MCP servers "
    "including an 11-tool Kubeflow MCP service and an agentic Credit Memo workflow backed by PostgreSQL "
    "on Kubernetes. I've also delivered an end-to-end RAG pipeline, from FAISS-based retrieval through "
    "LLM serving with Mistral-7B. I'm passionate about building AI systems that are reliable, "
    "explainable, and enterprise-ready."
)

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

PROJECTS = [
    ("HireLens — this website",
     "An interactive AI portfolio: a retrieval-augmented agent that answers recruiter questions "
     "from a profile knowledge base, with observable tool calls. Built with Streamlit, Python, "
     "and Hugging Face serverless inference. You're looking at it.",
     ["Agentic AI", "RAG", "Streamlit", "LLM eval"]),
    ("MCP Servers from Scratch (newsletter)",
     "A daily newsletter teaching engineers to build Model Context Protocol servers from zero. "
     "174 subscribers and growing — writing in public about MCP transports, tools, and security.",
     ["MCP", "Technical writing", "Community"]),
    ("Kubeflow MCP Server",
     "Production MCP service with 11 tools covering Kubeflow Pipelines and Notebooks, letting LLM "
     "agents operate ML platforms through natural language. Multi-tenant auth with OIDC/JWT and RBAC.",
     ["MCP", "FastMCP", "Kubernetes", "OIDC/JWT"]),
    ("Agentic Credit Memo workflow",
     "Tool-calling agent backend with FastMCP and PostgreSQL (CloudNativePG) on Kubernetes, "
     "automating document-generation workflows. Resolved service-mesh, TLS, and DNS issues to production.",
     ["Agentic AI", "PostgreSQL", "Kubernetes", "Helm"]),
]

QUESTION_CHIPS = {
    "Experience": ["What MCP work has Akbar done?",
                   "Tell me about his RAG experience",
                   "What did he build at HPE?"],
    "Skills": ["What are his strongest skills?",
               "Has he worked with Kubernetes and MLOps?",
               "What certifications does he have?"],
    "Contact": ["Is Akbar open to new opportunities?",
                "How can I reach Akbar?",
                "What is his contact info?"],
}

# ---------------------------------------------------------------- App

st.set_page_config(page_title="Akbar Shaik — Applied AI/ML Engineer",
                   page_icon=":robot_face:", layout="wide")

# Hero
st.title("Akbar Shaik")
st.subheader("Applied AI/ML Engineer · Agentic AI · LLMs & RAG · MCP · MLOps on Kubernetes")
st.write("I build production AI systems: MCP servers and tool-calling agents, RAG pipelines, "
         "and ML platforms on Kubernetes. 5+ years shipping agentic AI end to end.")

hero_c1, hero_c2, hero_c3 = st.columns(3)
cal_link = get_secret("CAL_LINK")
with hero_c1:
    if cal_link:
        st.link_button(":calendar: Schedule a call", cal_link)
    else:
        st.caption("Scheduling link coming soon")
with hero_c2:
    st.link_button(":briefcase: LinkedIn", "https://www.linkedin.com/in/akbar-shaik-388086356/")
with hero_c3:
    if cal_link:
        st.link_button(":calendar: Book intro call", cal_link)

st.divider()

tab_about, tab_exp, tab_skills, tab_projects, tab_chat, tab_call = st.tabs(
    ["About", "Experience", "Skills", "Projects", "Chat with my AI agent", "Schedule a call"])

with tab_about:
    st.markdown("### About me")
    st.write(ABOUT)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Experience", "5+ years")
    m2.metric("Skill areas", f"{sum(len(v) for v in SKILL_GROUPS.values())}+")
    m3.metric("Education", "M.S. Data Science")
    m4.metric("Certifications", "3")
    st.markdown("**Impact highlights**")
    st.write("- Automated 60% of support queries at 90%+ accuracy (RAG assistant)\n"
             "- 42% faster responses, 28% lower inference latency\n"
             "- 70% fewer model failures via MLOps practices\n"
             "- Shared MCP framework adopted across multiple engineering teams")

with tab_exp:
    st.markdown("### Professional experience")
    for title, company, dates, desc in EXPERIENCE:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.caption(f"{company} · {dates}")
            st.write(desc)
    st.markdown("### Education")
    st.write("- **M.S. Data Science**, University of North Texas\n"
             "- **B.Tech**, Lakireddy Bali Reddy College of Engineering")

with tab_skills:
    st.markdown("### Technical skills")
    for group, skills in SKILL_GROUPS.items():
        with st.expander(f"{group} ({len(skills)})"):
            cols = st.columns(3)
            for i, skill in enumerate(skills):
                cols[i % 3].markdown(f":white_check_mark: {skill}")

with tab_projects:
    st.markdown("### Projects")
    for name, desc, tags in PROJECTS:
        with st.container(border=True):
            st.markdown(f"**{name}**")
            st.write(desc)
            st.caption(" · ".join(tags))

with tab_chat:
    st.markdown("### Chat with my AI agent")
    st.caption("Ask anything about my background, skills, or projects. The agent searches my profile "
               "and answers from what it finds — watch the trace to see how it works.")
    col_chat, col_trace = st.columns([3, 2])

    if "history" not in st.session_state:
        st.session_state.history = []
    if "trace" not in st.session_state:
        st.session_state.trace = []
    if "pending_q" not in st.session_state:
        st.session_state.pending_q = None

    with col_chat:
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
        st.markdown("#### Agent trace")
        if not st.session_state.trace:
            st.info("Ask a question and watch the agent work here: retrieval first, then the answer.")
        else:
            for i, (title, detail) in enumerate(st.session_state.trace, 1):
                with st.expander(f"Step {i}: {title}", expanded=(i <= 2)):
                    st.write(detail)

with tab_call:
    st.markdown("### Schedule a call")
    st.write("Want to talk through a role or a project? Pick a time that works for you — "
             "you'll get a calendar invite automatically.")
    if cal_link:
        st.link_button(":calendar: Open the scheduler", cal_link)
        st.caption("Powered by Cal.com · 30-minute intro calls · Weekdays 2 – 4 PM CT")
    else:
        st.info("The scheduler is being set up — please check back soon.")

# Sidebar contact card
with st.sidebar:
    st.markdown("### Contact")
    st.write(":round_pushpin: Irving, Texas, USA")
    st.write(":briefcase: [LinkedIn](https://www.linkedin.com/in/akbar-shaik-388086356/)")
    st.write(":calendar: [Book an intro call](https://cal.com/akbar-shaik/intro-call)")
    st.divider()
    st.success("Open to new opportunities")
    st.divider()
    st.caption("Built by Akbar Shaik · HireLens")
