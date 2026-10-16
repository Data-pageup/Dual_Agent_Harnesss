multimodal_rag_poc/
│
├── config/
│   ├── models.py
│   └── settings.py
│
├── data/
│   ├── raw/
│   └── processed/
│       ├── text/
│       ├── charts/
│       ├── tables/
│       └── metadata/
│
├── src/
│   ├── ingestion/
│   │   ├── pdf_loader.py
│   │   ├── text_extractor.py
│   │   ├── chart_extractor.py
│   │   └── table_extractor.py
│   │
│   ├── processing/
│   │   ├── text_chunker.py
│   │   └── visual_summarizer.py
│   │
│   ├── retrieval/
│   │   ├── embeddings.py
│   │   └── pinecone_store.py
│   │
│   ├── generation/
│   │   ├── llm.py
│   │   └── vlm.py
│   │
│   ├── evaluation/
│   │   └── rag_evaluator.py
│   │
│   ├── graph/
│   │   └── workflow.py
│   │
│   └── main.py
│
├── .env
├── .gitignore
├── pyproject.toml
└── README.md