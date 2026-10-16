
from src.graph_pipeline.workflow import rag_workflow


def main():
    print("Multimodal RAG — type 'exit' to quit.")

    while True:
        question = input("\nQuestion: ").strip()

        if question.lower() in {"exit", "quit"}:
            break

        if not question:
            continue

        result = rag_workflow.invoke({"question": question})

        print("\nAnswer:")
        print(result["answer"])

        print("\nEvaluation:")
        print(result["evaluation"])


if __name__ == "__main__":
    main()
