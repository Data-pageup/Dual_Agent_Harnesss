## this is build pdf loader .

import pymupdf
from pathlib import Path  # this is a python inbuilt library that provides path class.


def load_pdf(pdf_path: str):
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError("File does not exist! ")

    if path.suffix.lower() != ".pdf":
        raise ValueError("there's no pdf file")

    document  = pymupdf.open(path)

    if document.is_encrypted:
        document.close()
        raise ValueError("the document is encrypted! ")

    return document
    





