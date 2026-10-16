
from pathlib import Path
from typing import Any

import chromadb
from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma_db"
COLLECTION_NAME = "multimodal_documents"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class ChromaStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DIR)
        )
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)

    def add_records(self, records: list[dict]) -> int:
        if not records:
            return 0

        documents = [record["text"] for record in records]
        embeddings = self.embedder.encode(
            documents,
            normalize_embeddings=True,
        ).tolist()

        ids = [
            f"{record['document_id']}_{record['source_type']}_"
            f"{record['page_number']}_{record['chunk_index']}"
            for record in records
        ]

        metadatas = [
            {
                key: value
                for key, value in record.items()
                if key not in {"text"} and isinstance(
                    value, (str, int, float, bool)
                )
            }
            for record in records
        ]

        # Upsert makes rerunning ingestion safe for existing IDs.
        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        return len(records)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        query_embedding = self.embedder.encode(
            [query],
            normalize_embeddings=True,
        ).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=min(top_k, max(self.collection.count(), 1)),
            include=["documents", "metadatas", "distances"],
        )

        matches = []
        for i, document in enumerate(results["documents"][0]):
            matches.append({
                "text": document,
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            })

        return matches
