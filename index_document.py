from src.ingestion_pipeline.pdf_loader import load_pdf
from src.ingestion_pipeline.text_extractor import extract_text
from src.ingestion_pipeline.table_extractor import extract_tables
from src.ingestion_pipeline.chart_extractor import extract_charts

from src.processing_pipeline.visual_summarizer import summarize_extracted_images
from src.processing_pipeline.text_chunker import chunk_text
from src.processing_pipeline.document_processing import process_document

from src.storage.artifact_store import save_json

from src.retrieval_pipeline.chroma_store import ChromaStore

from src.generation_pipeline.llm import generate_answer
from src.evaluation_pipeline.rag_evaluator import evaluate_answer
from src.graph_pipeline.workflow import rag_workflow 
from src.ingestion_pipeline.pdf_loader import load_pdf
from src.ingestion_pipeline.text_extractor import extract_text
from src.ingestion_pipeline.table_extractor import extract_tables
from src.ingestion_pipeline.chart_extractor import extract_charts

from src.processing_pipeline.visual_summarizer import summarize_extracted_images
from src.processing_pipeline.text_chunker import chunk_text
from src.processing_pipeline.document_processing import process_document

from src.storage.artifact_store import save_json

from src.retrieval_pipeline.chroma_store import ChromaStore

from src.generation_pipeline.llm import generate_answer
from src.evaluation_pipeline.rag_evaluator import evaluate_answer
from src.graph_pipeline.workflow import rag_workflow

DOCUMENT_ID = "NovaCore_Multimodal_Company_Report_2026"


def main():
    print("Preparing document records...")

    records = process_document(DOCUMENT_ID)
    print(f"Records prepared: {len(records)}")

    store = ChromaStore()
    indexed = store.add_records(records)

    print(f"Records indexed: {indexed}")
    print(f"Total records in ChromaDB: {store.collection.count()}")


if __name__ == "__main__":
    main()
