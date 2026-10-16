
from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_text(
    extracted_pages: list[dict],
    document_id: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> list[dict]:
    """
    Split extracted PDF text into chunks while preserving source metadata.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )

    chunks = []

    for page in extracted_pages:
        page_number = page["page_number"]
        page_text = page["text"].strip()

        if not page_text:
            continue

        page_chunks = splitter.split_text(page_text)

        for chunk_index, chunk in enumerate(page_chunks, start=1):
            chunks.append(
                {
                    "document_id": document_id,
                    "page_number": page_number,
                    "chunk_index": chunk_index,
                    "text": chunk,
                    "source_type": "text",
                }
            )

    return chunks
