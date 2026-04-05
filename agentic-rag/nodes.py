from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from retriever import retriever
from state import GraphState, SubQuery

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def decompose(state: GraphState) -> dict:
    prompt = (
        f"Break this question into 2-3 independent sub-questions.\n"
        f"One per line, nothing else.\n\nQuestion: {state['original_query']}"
    )
    lines = llm.invoke(prompt).content.strip().split("\n")
    return {"sub_queries": [SubQuery(query=q.strip()) for q in lines if q.strip()]}


def retrieve_and_grade(state: GraphState) -> dict:
    for sq in state["sub_queries"]:
        if sq.is_relevant:
            continue
        docs = retriever.invoke(sq.query)
        sq.docs = [d.page_content for d in docs]
        grade_msg = f"Relevant to '{sq.query}'?\nDocs: {' '.join(sq.docs)}\nYES or NO."
        if "yes" in llm.invoke(grade_msg).content.lower():
            sq.is_relevant = True
        else:
            sq.retry_count += 1
            sq.query = llm.invoke(
                f"Rewrite for better results: {sq.query}"
            ).content.strip()
    return {"sub_queries": state["sub_queries"]}


def synthesize(state: GraphState) -> dict:
    all_docs = []
    for sq in state["sub_queries"]:
        all_docs.extend(sq.docs)
    context = "\n\n".join(all_docs)
    response = llm.invoke(
        f"Answer using only this context.\n\n"
        f"Context:\n{context}\n\nQuestion: {state['original_query']}"
    )
    return {"final_answer": response.content}
