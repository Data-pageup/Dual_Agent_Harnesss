
import pymupdf
from pathlib import Path

from src.ingestion_pipeline.pdf_loader import load_pdf


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHARTS_DIR = PROJECT_ROOT / "data" / "processed" / "charts"


def extract_charts(pdf_path: str) -> list[dict]:
    """
    Extract embedded images from a PDF and save them to disk.

    Args:
        pdf_path: Path to the source PDF.

    Returns:
        A list containing metadata for every extracted image.
    """
    document = load_pdf(pdf_path)
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    extracted_images = []

    try:
        for page_number, page in enumerate(document, start=1):
            images = page.get_images(full=True)

            for image_index, image in enumerate(images, start=1):
                xref = image[0]

                image_info = document.extract_image(xref)

                image_bytes = image_info["image"]
                image_ext = image_info["ext"]

                image_name = (
                    f"page_{page_number}_image_{image_index}.{image_ext}"
                )

                image_path = CHARTS_DIR / image_name
                image_path.write_bytes(image_bytes)

                extracted_images.append({
                    "page_number": page_number,
                    "image_name": image_name,
                    "image_path": str(image_path),
                    "extension": image_ext,
                    "xref": xref,
                })

    finally:
        document.close()

    return extracted_images
