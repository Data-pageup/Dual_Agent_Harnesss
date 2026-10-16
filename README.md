# Multimodal RAG (Groq + ChromaDB)

A Retrieval-Augmented Generation pipeline that indexes **text, tables, and charts/images** from PDF reports into a single searchable store, then answers questions with mandatory source citations — and evaluates whether those citations actually hold up before trusting the answer.

Built as a proof of concept using [NovaCore Systems Ltd.](./data/processed/text) — a fictional company report — as the sample document.

## Why this is different from a basic RAG demo

Most RAG pipelines stop at retrieve → generate. This one adds a third stage:

- **Retrieve** — pull the most relevant text chunks, table rows, and chart/image descriptions from ChromaDB
- **Generate** — answer strictly from retrieved evidence, with `[Source N]` citations required
- **Evaluate** — check whether citations are present, whether they're valid, and whether the retrieved context was sufficient — flagging the answer for review if not

Charts and embedded images aren't skipped or treated as decoration — they're summarized by a vision model and indexed alongside the text, so a question like *"what does the revenue chart show?"* is answerable from the same index as a question about a paragraph of prose.

## Architecture

```
PDF report
   │
   ▼
┌─────────────────────────────────────────┐
│  Ingestion (PyMuPDF)                     │
│  text_extractor · table_extractor        │
│  chart_extractor (embedded images)       │
└─────────────────┬─────────────────────────┘
                   ▼
┌─────────────────────────────────────────┐
│  Processing                              │
│  text_chunker      → chunked text        │
│  visual_summarizer → vision-model         │
│                       descriptions        │
│                       of every image      │
└─────────────────┬─────────────────────────┘
                   ▼
┌─────────────────────────────────────────┐
│  Storage (data/processed/*.json)         │
└─────────────────┬─────────────────────────┘
                   ▼
┌─────────────────────────────────────────┐
│  Retrieval (ChromaDB + Sentence-         │
│  Transformers) — one unified index for   │
│  text, table text, and visual summaries  │
└─────────────────┬─────────────────────────┘
                   ▼
┌─────────────────────────────────────────┐
│  LangGraph workflow                      │
│  retrieve → generate → evaluate          │
│  generation via Groq LLM                 │
│  evaluation checks citation validity     │
└─────────────────────────────────────────┘
```

## Project structure

```
multimodal-rag-groq/
├── data/
│   └── processed/
│       ├── text/          # extracted page text (JSON)
│       ├── tables/        # extracted tables (JSON)
│       ├── charts/        # extracted chart/image files
│       └── metadata/      # vision-model summaries of charts/images
├── src/
│   ├── ingestion_pipeline/
│   │   ├── pdf_loader.py
│   │   ├── text_extractor.py
│   │   ├── table_extractor.py
│   │   └── chart_extractor.py
│   ├── processing_pipeline/
│   │   ├── text_chunker.py
│   │   ├── visual_summarizer.py
│   │   └── document_processing.py
│   ├── storage/
│   │   └── artifact_store.py
│   ├── retrieval_pipeline/
│   │   └── chroma_store.py
│   ├── generation_pipeline/
│   │   └── llm.py
│   ├── evaluation_pipeline/
│   │   └── rag_evaluator.py
│   └── graph_pipeline/
│       └── workflow.py
├── main.py              # extracts + summarizes charts/images from a PDF
├── index_document.py    # chunks + embeds + indexes everything into ChromaDB
├── ask.py               # interactive Q&A loop (retrieve → generate → evaluate)
├── requirements.txt
├── pyproject.toml
└── .env.example
```

## Setup

**1. Create a virtual environment and install dependencies**

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

**2. Configure your API key**

```bash
cp .env.example .env
```

Edit `.env` and set `GROQ_API_KEY` (free key at [console.groq.com/keys](https://console.groq.com/keys)).

Groq's model lineup changes over time — if a model ID 404s, check [console.groq.com/docs/models](https://console.groq.com/docs/models) and update `GROQ_TEXT_MODEL` / `GROQ_VISION_MODEL` in `.env` rather than editing the code.

## Usage

Run in order:

```bash
# 1. Extract and summarize charts/images from a PDF
#    (edit the hardcoded PDF path in main.py first)
python main.py

# 2. Chunk text + tables + visual summaries, embed, and index into ChromaDB
python index_document.py

# 3. Ask questions interactively
python ask.py
```

Since `data/processed/` already ships with extracted text, tables, and visual summaries for the sample NovaCore report, you can skip straight to steps 2 and 3 to query it right away.

### Example

```
Question: What was NovaCore's 2026 revenue and operating margin?

Answer:
NovaCore's 2026 revenue was $132.0M, with an operating margin of 18.4% [Source 1].

Evaluation:
{'answer_present': True, 'context_retrieved': True, 'citation_count': 1,
 'citations_valid': True, 'needs_review': False}
```

## How evaluation works

`rag_evaluator.py` doesn't judge factual correctness — it checks the *structural integrity* of the answer:

- Was any context retrieved at all?
- Did the model actually cite its sources (`[Source N]`)?
- Do those citation numbers correspond to real retrieved sources?

If any of these fail, `needs_review` is set to `True`, signaling the answer shouldn't be trusted without a human check — rather than silently returning an unsupported or hallucinated response.

## Tech stack

| Layer | Tool |
|---|---|
| PDF parsing | PyMuPDF |
| Text chunking | LangChain Text Splitters |
| Vision summarization | Groq (`qwen/qwen3.8-27b`) |
| Text generation | Groq (`openai/gpt-oss-120b`) |
| Embeddings | Sentence-Transformers (`all-MiniLM-L6-v2`) |
| Vector store | ChromaDB |
| Orchestration | LangGraph |

## License

Add a license of your choice (MIT is a common default for POCs like this).
