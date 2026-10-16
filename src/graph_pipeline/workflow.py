
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from src.retrieval_pipeline.chroma_store import ChromaStore
from src.generation_pipeline.llm import generate_answer
from src.evaluation_pipeline.rag_evaluator import evaluate_answer


class RAGState(TypedDict, total=False):
    question: str
    context: list[dict]
    answer: str
    evaluation: dict


store = ChromaStore()


def retrieve_node(state: RAGState) -> dict:
    context = store.search(state["question"], top_k=5)
    return {"context": context}


def generate_node(state: RAGState) -> dict:
    answer = generate_answer(
        state["question"],
        state.get("context", []),
    )
    return {"answer": answer}


def evaluate_node(state: RAGState) -> dict:
    evaluation = evaluate_answer(
        state.get("answer", ""),
        state.get("context", []),
    )
    return {"evaluation": evaluation}


builder = StateGraph(RAGState)

builder.add_node("retrieve", retrieve_node)
builder.add_node("generate", generate_node)
builder.add_node("evaluate", evaluate_node)

builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", "evaluate")
builder.add_edge("evaluate", END)

rag_workflow = builder.compile()
