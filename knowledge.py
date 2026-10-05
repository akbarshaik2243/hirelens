"""Structured profile facts about Akbar Shaik, sourced from his resume.

The agent searches these facts (tool: search_profile) and answers
recruiter questions using only what it finds here.
"""

PROFILE = {
    "name": "Akbar Shaik",
    "title": "Applied AI / ML Engineer",
    "focus": "Agentic AI, LLMs & RAG, MCP, MLOps on Kubernetes",
    "location": "Irving, Texas, USA",
    "experience_years": "5+ years",
    "availability": "Open to new opportunities. Contact Akbar directly to discuss fit.",
    "education": "M.S. Data Science, University of North Texas; B.Tech, Lakireddy Bali Reddy College of Engineering",
}

FACTS = [
    ("summary",
     "Applied AI/ML Engineer with 5+ years shipping production agentic AI, LLM, and MLOps systems end to end. "
     "Builds Model Context Protocol (MCP) servers and tool-calling agents that let LLMs safely operate real enterprise platforms; "
     "designs RAG and GraphRAG systems with hybrid retrieval, evaluation, and guardrails; fine-tunes models with LoRA, PEFT, and DPO. "
     "Deep cloud-native strength in Kubernetes, Helm, autoscaling, and multi-tenant security (OIDC/JWT, RBAC) across AWS, Azure, and GCP."),

    ("impact",
     "Proven impact: automated 60% of support queries at 90%+ accuracy, 42% faster responses, "
     "70% fewer model failures, and 28% lower inference latency."),

    ("experience_hpe",
     "Applied Machine Learning Engineer at Hewlett Packard Enterprise (HPE), Texas, Apr 2026 to Present. "
     "Designed and built a Model Context Protocol (MCP) server with ~30 tools letting LLM agents manage ML pipelines, "
     "experiments, runs, and notebooks on a Kubernetes-based AI platform through natural language. "
     "Implemented multi-tenant authentication with OIDC/JWT, least-privilege RBAC, and namespace-level isolation. "
     "Co-designed a shared Python framework for MCP servers (async HTTP client, typed error handling, auth middleware, "
     "Redis caching, OpenTelemetry hooks) adopted across multiple engineering teams. "
     "Built a tool-calling agent backend with FastMCP and PostgreSQL on Kubernetes for document-generation workflows. "
     "Built an agent evaluation harness with DeepEval and Promptfoo scoring tool-selection accuracy, step trajectories, "
     "and response faithfulness. Applied OWASP Top 10 for LLM Applications practices: prompt-injection defense, "
     "NeMo Guardrails, Llama Guard, red-team testing. Built an end-to-end RAG pipeline with hybrid TF-IDF + FAISS retrieval "
     "and a Gradio UI, served by Mistral-7B-Instruct. Benchmarked LLM serving on NVIDIA NIM, Triton, and vLLM."),

    ("experience_teledyne",
     "Applied AI Engineer at Teledyne Technologies Inc., Jan 2024 to Apr 2026. "
     "Designed a document-grounded RAG assistant with LangChain, FAISS, and GPT-4, automating 60% of Tier-1 queries "
     "with 90%+ answer accuracy and 42% faster response times. Deployed low-latency LLM inference APIs with FastAPI, "
     "Docker, and AWS Lambda. Fine-tuned GPT-based models with LoRA/PEFT, improving domain-adaptation speed by 35%. "
     "Built safety layers: PII masking, policy validation, SVM fallback classifier for high-risk inputs. "
     "Built GraphRAG over policy and claims entities in Neo4j, combining graph traversal with Pinecone/Qdrant vector search "
     "and Elasticsearch BM25 for multi-hop QA. Aligned domain models with DPO on curated preference pairs. "
     "Shipped GenAI workloads on AWS Bedrock and Azure OpenAI, optimizing inference with TensorRT-LLM and SGLang."),

    ("experience_creative",
     "MLOps Engineer / ML Platform Engineer at Creative Newtech Ltd, India, Feb 2020 to Aug 2022. "
     "Built MLflow-integrated pipelines with full training-to-deployment lineage. Enforced CI/CD with GitHub Actions "
     "and the MLflow Model Registry. Automated drift detection (KS test, PSI) and SHAP/LIME explanations; "
     "reduced model failures by 70%. Optimized inference with ONNX Runtime, cutting API latency by 28%. "
     "Passed 2 regulatory audits with zero issues. Scaled feature engineering with Ray and Databricks (Spark), "
     "sourcing data from Snowflake. Real-time scoring on Kafka streams via Triton Inference Server, "
     "infrastructure with Terraform and Argo CD GitOps."),

    ("skills_agentic",
     "Agentic AI: Model Context Protocol (MCP), FastMCP, tool/function calling, multi-agent orchestration, "
     "ReAct and planner-executor patterns, LangChain, LangGraph, CrewAI, OpenAI Agents SDK, A2A, Google ADK, "
     "Vertex AI Agent Builder, AWS Bedrock AgentCore, Claude API, agent memory and state, human-in-the-loop."),

    ("skills_llm",
     "LLMs & GenAI: OpenAI GPT-4 family, Mistral-7B, Qwen, Llama, Hugging Face Transformers, prompt engineering, "
     "structured outputs, LoRA/PEFT, DPO, RLHF, Unsloth, DeepSpeed/FSDP, synthetic data, quantization, PII masking, "
     "AWS Bedrock, Azure OpenAI, Whisper, vision-language models."),

    ("skills_rag",
     "RAG & Retrieval: chunking strategies, embeddings (Sentence-BERT), hybrid search (BM25 + dense), re-ranking, "
     "GraphRAG, Neo4j, FAISS, Pinecone, Qdrant, Milvus, ChromaDB, Weaviate, pgvector, Elasticsearch/OpenSearch, "
     "Docling, Unstructured, incremental ingestion, Confluence/GitHub connectors."),

    ("skills_mlops",
     "Model Serving & MLOps: KServe, vLLM, SGLang, TensorRT-LLM, Triton, NVIDIA NIM, FastAPI, MLflow, Kubeflow Pipelines "
     "and Notebooks, Katib, Airflow, Apache Spark, Ray, Databricks, Snowflake, Kafka, ONNX Runtime, A/B testing, "
     "drift detection, CI/CD (GitHub Actions, Jenkins)."),

    ("skills_platform",
     "Cloud-Native & Platform: Kubernetes, Helm, Docker, Istio, Harbor, HPA autoscaling, RBAC, Keycloak/OIDC, "
     "JWT/JWKS, CloudNativePG, Redis, AWS (SageMaker, Lambda, ECS, EKS, S3), Azure ML, GCP Vertex AI, Terraform, Argo CD."),

    ("skills_eval",
     "Agent Evaluation & Safety: DeepEval, Promptfoo, RAGAS, LLM-as-judge, trajectory and tool-use evaluation, "
     "red-teaming, prompt-injection defense, OWASP LLM Top 10, NeMo Guardrails, Llama Guard."),

    ("skills_observability",
     "Observability & Governance: OpenTelemetry, Langfuse, LangSmith, Arize Phoenix, W&B Weave, Prometheus, Grafana, "
     "SHAP, LIME, model cards, AI governance, EU AI Act, NIST AI RMF, ISO/IEC 42001."),

    ("skills_languages",
     "Languages & Tools: Python (async, Pydantic, pytest), TypeScript/Node.js, SQL, Bash, REST APIs, PostgreSQL, "
     "MongoDB, MySQL, Git, Linux, Gradio, Streamlit, React."),

    ("certifications",
     "Certifications: AWS Certified Machine Learning Specialty, AWS Certified AI Practitioner, "
     "Google Data Analytics Professional Certificate."),

    ("contact",
     "To contact Akbar Shaik, use the 'Schedule a call' tab on this site to book a 30-minute "
     "intro call (weekdays 2-4 PM America/Chicago, Google Meet link emailed automatically). "
     "LinkedIn: linkedin.com/in/akbar-shaik-388086356"),

    ("projects",
     "Side projects: (1) HireLens — this site — an interactive AI portfolio: a retrieval-augmented agent "
     "that answers questions from a profile knowledge base with observable tool calls, built with Streamlit, "
     "Python, and Hugging Face serverless inference. (2) 'MCP Servers from Scratch' — a daily newsletter teaching "
     "engineers to build Model Context Protocol servers, with 174 subscribers."),

    ("identity",
     "Akbar Shaik is an Applied AI/ML Engineer with 5+ years of experience, based in Irving, Texas, USA. "
     "Master's in Data Science from the University of North Texas."),

    ("education",
     "Education: M.S. in Data Science from the University of North Texas; "
     "B.Tech from Lakireddy Bali Reddy College of Engineering."),

    ("career",
     "Career timeline: MLOps / ML Platform Engineer at Creative Newtech Ltd, India (Feb 2020 – Aug 2022); "
     "Applied AI Engineer at Teledyne Technologies Inc., US (Jan 2024 – Apr 2026); "
     "Applied Machine Learning Engineer at Hewlett Packard Enterprise (HPE), Texas (Apr 2026 – Present). "
     "5+ years total building production AI/ML systems end to end."),

    ("strengths",
     "Strengths evident from Akbar's track record: he ships production AI systems end to end, from design "
     "through deployment and scale; he builds shared frameworks and platforms that other engineering teams "
     "adopt; he owns hard production problems across networking, auth, and scale (service-mesh, TLS, DNS, "
     "autoscaling with zero pod restarts); his RAG and agent work holds up under rigorous evaluation "
     "(DeepEval, Promptfoo, RAGAS) and red-teaming; and his ML platforms have passed regulatory audits "
     "with zero issues."),

    ("work_style",
     "How Akbar works: production-first — evaluation harnesses gate prompt and tool changes before release; "
     "security-minded (OWASP LLM Top 10, guardrails, red-teaming, PII masking); builds documentation-grounded "
     "RAG with hybrid retrieval and failure analysis; cost-aware (tracks token cost and latency per request); "
     "collaborative — shared frameworks adopted across teams, demos to leadership, dogfooding with end users."),

    ("weaknesses",
     "On weaknesses: Akbar's profile doesn't list any weaknesses, so never invent any. What the record shows "
     "instead is how he handles gaps and risks: when a document-generation deployment hit service-mesh, TLS, "
     "and DNS issues, he resolved them to reach production; where agent quality was at risk, he built evaluation "
     "harnesses (DeepEval, Promptfoo) gating prompt and tool changes before release; where LLM safety was at "
     "risk, he added guardrails, red-teaming, and PII masking. Answer weakness questions from this evidence, "
     "in your own words, and never append a booking link."),

    ("skills_mldl",
     "ML & Deep Learning: PyTorch, TensorFlow, Keras, scikit-learn, XGBoost, distributed training "
     "(PyTorch DDP), NLP (NER, summarization, Q&A, intent classification), feature engineering, "
     "model evaluation, predictive maintenance modeling, recommendation systems."),

    ("availability",
     "Akbar offers 30-minute intro calls on working days (Monday-Friday), 2:00 PM to 4:00 PM America/Chicago. "
     "Book directly through the 'Schedule a call' tab on this site (powered by Cal.com); every booking "
     "automatically generates a Google Meet link emailed to both sides."),
]
