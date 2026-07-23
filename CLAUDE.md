# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

This is a step-by-step LangChain teaching project, built incrementally as a series of small, numbered example scripts. Each script corresponds to one concept and is documented in detail in `TUTORIAL.md`, which is the source of truth for *why* each piece of code is written the way it is — read it before making changes to any numbered script.

- LLM provider: DeepSeek, accessed through `langchain_openai.ChatOpenAI` with `base_url="https://api.deepseek.com/v1"` and `model="deepseek-chat"` (DeepSeek's API is OpenAI-compatible, so this is the standard `ChatOpenAI` class, not a DeepSeek-specific SDK).
- Dependency management: plain `pip` + `requirements.txt` with pinned versions (chosen deliberately for a teaching repo — reproducibility over convenience).
- Embeddings (RAG step only): local, free HuggingFace model `BAAI/bge-small-zh-v1.5` via `langchain_huggingface.HuggingFaceEmbeddings`, paired with `langchain_core.vectorstores.InMemoryVectorStore` (not FAISS/Chroma — `langchain-community` is being sunset upstream and was deliberately avoided).

## Commands

```powershell
# Install dependencies into the existing .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt

# Run any numbered example (Windows console needs PYTHONUTF8=1 or Chinese output mojibake's)
$env:PYTHONUTF8=1; .venv/Scripts/python.exe 03_first_llm_call.py
```

Requires a `.env` file (git-ignored) with `DEEPSEEK_API_KEY=...` — see `.env.example` for the template.

## Structure

- `NN_topic.py` — one numbered script per tutorial step (`03_first_llm_call.py` through `09_rag.py`). Each is a standalone, runnable file, not a shared library — there's no shared `src/` module; later scripts don't import from earlier ones.
- `TUTORIAL.md` — the running curriculum: an outline table tracking step status, plus a `做了什么` / `为什么这样做` section per step. **This must be updated alongside every new numbered script** — that's the core convention of this repo, not optional documentation.
- `data/` — fixture text files used by the RAG step (e.g. `company_faq.txt`, deliberately fictional so retrieval correctness can be verified — if the LLM answers correctly, it's because retrieval worked, not because it already knew the answer).
- `main.py` — leftover default PyCharm template, unrelated to the tutorial.

## Conventions established so far

- Every script re-declares its own `ChatOpenAI` instance (no shared client module) — keeps each numbered file copy-paste runnable in isolation, matching the teaching goal of one concept per file.
- New steps build on the previous script's code (e.g. the same translation prompt reappears across steps 4–6) so the reader sees the same example evolve rather than juggling unrelated ones.
- No standalone verification/check scripts are kept around after a step is confirmed working — see git history for examples of these being removed once their one-time purpose was served.
- When a library default doesn't work against DeepSeek specifically (e.g. `with_structured_output`'s default `response_format` method 400s on DeepSeek — use `method="function_calling"` instead), the workaround and reason are recorded in `TUTORIAL.md`, not just fixed silently.
