
from src.ingestion_pipeline.pdf_loader import load_pdf


def extract_tables(pdf_path: str) -> list:
    document = load_pdf(pdf_path)
    extracted_tables = []

    for page_number, page in enumerate(document):
        tables = page.find_tables()

        for t in tables.tables:
            table_data = t.extract()

            extracted_tables.append({
                "page_number": page_number + 1,
                "table_data": table_data
            })

    document.close()

    return extracted_tables
