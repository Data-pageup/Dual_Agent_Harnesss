
import json
from pathlib import Path

from src.processing_pipeline.text_chunker import chunk_text


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def load_json(file_path: Path) -> dict:
    """Load a JSON artifact from disk."""
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def process_document(document_id: str) -> list[dict]:
    """
    Normalize text chunks, tables, and visual summaries
    into a common record format.
    """

    records = []

    # 1. Load extracted text and create metadata-preserving chunks
    text_path = PROCESSED_DIR / "text" / f"{document_id}.json"
    text_data = load_json(text_path)

    text_chunks = chunk_text(
        extracted_pages=text_data["pages"],
        document_id=document_id,
    )

    records.extend(text_chunks)

    # 2. Load tables and convert each table into searchable text
    table_path = PROCESSED_DIR / "tables" / f"{document_id}.json"
    table_data = load_json(table_path)

    for index, table in enumerate(table_data.get("tables", []), start=1):
        table_rows = table.get("table_data", [])

        table_text = "\n".join(
            " | ".join(
                "" if cell is None else str(cell)
                for cell in row
            )
            for row in table_rows
        )

        if table_text.strip():
            records.append({
                "document_id": document_id,
                "page_number": table["page_number"],
                "chunk_index": index,
                "source_type": "table",
                "text": f"Table content:\n{table_text}",
            })

    # 3. Load visual summaries
    visual_path = (
        PROCESSED_DIR
        / "metadata"
        / f"{document_id}_visual_summaries.json"
    )

    if visual_path.exists():
        visual_data = load_json(visual_path)

        for index, visual in enumerate(
            visual_data.get("summaries", []),
            start=1,
        ):
            description = visual.get("description", "").strip()

            if description:
                records.append({
                    "document_id": document_id,
                    "page_number": visual["page_number"],
                    "chunk_index": index,
                    "source_type": "visual",
                    "text": (
                        f"Visual description of "
                        f"{visual['image_name']}:\n{description}"
                    ),
                })

    return records
