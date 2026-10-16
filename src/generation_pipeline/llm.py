import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

MODEL_NAME = os.getenv(
    "GROQ_TEXT_MODEL",
    "openai/gpt-oss-120b",
)


def generate_answer(question: str, context: list[dict]) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY is missing.")

    if not context:
        return "I couldn't find relevant evidence in the indexed documents."

    evidence = "\n\n".join(
        (
            f"[Source {i}] "
            f"Document: {item['metadata'].get('document_id', 'unknown')}; "
            f"Page: {item['metadata'].get('page_number', 'unknown')}; "
            f"Type: {item['metadata'].get('source_type', 'unknown')}\n"
            f"{item['text']}"
        )
        for i, item in enumerate(context, start=1)
    )

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": (
                    "Answer using only the supplied evidence. "
                    "If the evidence is insufficient, say so. "
                    "Do not invent facts or numerical values. "
                    "Cite supporting sources using [Source N]. Answer in short."
                ),
            },
            {
                "role": "user",
                "content": f"Question:\n{question}\n\nEvidence:\n{evidence}",
            },
        ],
    )

    return response.choices[0].message.content or "No answer generated."
