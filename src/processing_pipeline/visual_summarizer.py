import base64
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from src.storage.artifact_store import save_json


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHARTS_DIR = PROJECT_ROOT / "data" / "processed" / "charts"

load_dotenv(PROJECT_ROOT / ".env")

MODEL_NAME = os.getenv(
    "GROQ_VISION_MODEL",
    "meta-llama/llama-4-scout-17b-16e-instruct",
)


def encode_image(image_path: Path) -> str:
    """Encode an image as Base64 for the vision API."""
    with image_path.open("rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def summarize_image(image_path: Path, client: Groq) -> str:
    """Generate a factual description of an extracted PDF image."""
    extension = image_path.suffix.lower()

    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }

    mime_type = mime_types.get(extension)

    if mime_type is None:
        raise ValueError(f"Unsupported image format: {extension}")

    encoded_image = encode_image(image_path)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Analyze this image extracted from a PDF report. "
                            "If it contains a chart or graph, describe its "
                            "title, axes, units, trends, comparisons, and "
                            "visible values. If it contains a table, describe "
                            "its headers and key values. Otherwise, describe "
                            "its relevant visual content. Do not invent values "
                            "or information that cannot be read. Mention "
                            "uncertainties explicitly.give all in short. "
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": (
                                f"data:{mime_type};base64,{encoded_image}"
                            )
                        },
                    },
                ],
            }
        ],
        temperature=0.1,
        max_tokens=800,
    )

    description = response.choices[0].message.content

    if not description:
        raise ValueError(f"Empty vision response for {image_path.name}")

    return description.strip()


def summarize_extracted_images(
    image_records: list[dict],
    document_id: str,
) -> list[dict]:
    """Summarize extracted images and persist the resulting metadata."""
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY is missing. Add it to your project .env file."
        )

    client = Groq(api_key=api_key)
    summaries = []

    for record in image_records:
        image_path = Path(record["image_path"])

        if not image_path.is_absolute():
            image_path = PROJECT_ROOT / image_path

        if not image_path.is_file():
            print(f"Skipping missing image: {image_path}")
            continue

        try:
            print(f"Summarizing: {image_path.name}")

            description = summarize_image(image_path, client)

            summaries.append(
                {
                    "document_id": document_id,
                    "page_number": record["page_number"],
                    "image_name": record["image_name"],
                    "image_path": str(image_path),
                    "description": description,
                }
            )

        except Exception as exc:
            print(f"Failed to summarize {image_path.name}: {exc}")

    output_file = save_json(
        {
            "document_id": document_id,
            "total_images": len(image_records),
            "successful_summaries": len(summaries),
            "summaries": summaries,
        },
        category="metadata",
        filename=f"{document_id}_visual_summaries.json",
    )

    print(f"Visual summaries saved to: {output_file}")

    return summaries
