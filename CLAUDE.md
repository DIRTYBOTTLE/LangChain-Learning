# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

This is a step-by-step LangChain + LangGraph teaching project, built incrementally as a series of small, numbered example scripts. Each script corresponds to one concept and is documented in detail in `TUTORIAL.md`, which is the source of truth for *why* each piece of code is written the way it is — read it before making changes to any numbered script.

The curriculum has two parts:

- **LangChain (steps 1–12)**: env setup through prompts, LCEL, output parsing, memory, tool calling/agents, RAG, streaming, persistent vector store, and a capstone chatbot app.
- **LangGraph (steps 13–17, no numeric gap — continues at `13_langgraph_basics.py`)**: State/Node/Edge fundamentals (deliberately LLM-free), conditional edges, an LLM node, a hand-rolled tool-calling loop that reimplements what `create_agent` does under the hood, and the `Checkpointer` mechanism as the official replacement for the hand-maintained history list from step 7/15.

- LLM provider: DeepSeek, accessed through `langchain_openai.ChatOpenAI` with `base_url="https://api.deepseek.com/v1"` and `model="deepseek-chat"` (DeepSeek's API is OpenAI-compatible, so this is the standard `ChatOpenAI` class, not a DeepSeek-specific SDK).
- Dependency management: plain `pip` + `requirements.txt` with pinned versions (chosen deliberately for a teaching repo — reproducibility over convenience). Every package directly `import`-ed by a script must be listed explicitly, even if it would already be pulled in transitively by another dependency (e.g. `langgraph` and `grandalf` were initially missing despite working, because `langchain`'s `create_agent` happened to pull `langgraph` in already — this was a real bug, not just style).
- Embeddings (RAG steps only): local, free HuggingFace model `BAAI/bge-small-zh-v1.5` via `langchain_huggingface.HuggingFaceEmbeddings`, paired with `langchain_core.vectorstores.InMemoryVectorStore` (not FAISS/Chroma — `langchain-community` is being sunset upstream and was deliberately avoided). Persistence (step 11) uses `InMemoryVectorStore.dump()/load()` plus an md5 hash of the source doc to detect staleness — an mtime-based check was considered and rejected as less reliable.

## Commands

```powershell
# Install dependencies into the existing .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt

# Run any numbered example (Windows console needs PYTHONUTF8=1 or Chinese output mojibake's)
$env:PYTHONUTF8=1; .venv/Scripts/python.exe 03_first_llm_call.py
```

Requires a `.env` file (git-ignored) with `DEEPSEEK_API_KEY=...` — see `.env.example` for the template.

## Structure

- `NN_topic.py` — one numbered script per tutorial step (`03_first_llm_call.py` through `17_langgraph_checkpointer.py`). Each is a standalone, runnable file, not a shared library — there's no shared `src/` module; later scripts don't import from earlier ones (some deliberately duplicate a helper function across files, e.g. the vector-store load/build logic in steps 11 and 12 — see the convention below).
- `TUTORIAL.md` — the running curriculum: an outline table tracking step status, plus a `做了什么` / `为什么这样做` section per step. **This must be updated alongside every new numbered script** — that's the core convention of this repo, not optional documentation.
- `data/` — fixture text files used by the RAG steps (e.g. `company_faq.txt`, deliberately fictional so retrieval correctness can be verified — if the LLM answers correctly, it's because retrieval worked, not because it already knew the answer).
- `vector_store.json` / `vector_store.hash` — generated artifacts from the persistence step, git-ignored; regenerate by running `11_persistent_vector_store.py` or `12_chatbot_app.py`.
- `main.py` — leftover default PyCharm template, unrelated to the tutorial.

## Conventions established so far

- Every script re-declares its own `ChatOpenAI` instance (no shared client module) — keeps each numbered file copy-paste runnable in isolation, matching the teaching goal of one concept per file.
- New steps build on the previous script's code (e.g. the same translation prompt reappears across steps 4–6) so the reader sees the same example evolve rather than juggling unrelated ones.
- No standalone verification/check scripts are kept around after a step is confirmed working — see git history for examples of these being removed once their one-time purpose was served.
- When a library default doesn't work against DeepSeek specifically (e.g. `with_structured_output`'s default `response_format` method 400s on DeepSeek — use `method="function_calling"` instead), the workaround and reason are recorded in `TUTORIAL.md`, not just fixed silently.
