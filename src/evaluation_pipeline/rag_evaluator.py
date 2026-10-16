
import re


def evaluate_answer(answer: str, context: list[dict]) -> dict:
    citations = re.findall(r"\[Source (\d+)\]", answer)

    valid_source_numbers = {
        str(index)
        for index in range(1, len(context) + 1)
    }

    valid_citations = sorted(
        set(citations) & valid_source_numbers,
        key=int,
    )

    return {
        "answer_present": bool(answer.strip()),
        "context_retrieved": bool(context),
        "citation_count": len(valid_citations),
        "citations_valid": all(
            citation in valid_source_numbers
            for citation in citations
        ),
        "needs_review": (
            not answer.strip()
            or not context
            or not citations
            or any(
                citation not in valid_source_numbers
                for citation in citations
            )
        ),
    }
