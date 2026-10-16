from pathlib import Path

from src.ingestion_pipeline.chart_extractor import extract_charts
from src.processing_pipeline.visual_summarizer import (
    summarize_extracted_images,
)

pdf_path = Path(
    r"C:\Users\admin\Downloads\NovaCore_Multimodal_Company_Report_2026.pdf"
)

document_id = pdf_path.stem

# Step 1: Extract images from the PDF
extracted_images = extract_charts(str(pdf_path))

print(f"Images extracted: {len(extracted_images)}")

if not extracted_images:
    print("No embedded images found to summarize.")
    raise SystemExit(0)

# Step 2: Summarize the extracted images using the vision model
visual_summaries = summarize_extracted_images(
    image_records=extracted_images,
    document_id=document_id,
)

# Step 3: Display results
print(f"\nVisual summaries generated: {len(visual_summaries)}")

for summary in visual_summaries:
    print(f"\nPage: {summary['page_number']}")
    print(f"Image: {summary['image_name']}")
    print(f"Description: {summary['description']}")
