---
title: HireLens
emoji: "\U0001F916"
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
---

# HireLens — AI profile agent

An agentic demo by **Akbar Shaik** (Applied AI/ML Engineer).

Ask anything about Akbar's background: MCP servers, agentic AI, RAG systems,
MLOps on Kubernetes, availability for remote contract roles. The agent searches
his profile knowledge base with a `search_profile` tool call, then an LLM
composes the answer strictly from the retrieved facts. The agent trace panel
shows every step.

**Recruiters:** akbarshaik2243@gmail.com · (469) 629-9816 · Irving, Texas

Setup: add a free Hugging Face token as the `HF_TOKEN` Space secret
(Settings → Variables and secrets) to enable the inference API.
