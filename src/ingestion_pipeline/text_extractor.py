import pymupdf    # opens pdfs extract text from pages.


from src.ingestion_pipeline.pdf_loader import load_pdf


def extract_text(path_file: str):
    document = load_pdf(path_file)
    extracted_pages = []   # this empty list will store the text and page number

    for page_number,page in enumerate(document):   # page_number like 0,1 . page is the current page
        text = page.get_text()

        extracted_pages.append({"page_number":page_number+1,
                                "text":text})

    document.close()

    return extracted_pages



    
        

