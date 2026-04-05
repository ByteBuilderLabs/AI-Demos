from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

docs = [
    Document(page_content="LangGraph models workflows as state machines where nodes are functions that read and write to shared state."),
    Document(page_content="ChromaDB stores vector embeddings locally and supports fast approximate nearest neighbor search via HNSW."),
    Document(page_content="Query decomposition splits complex questions into sub-questions that can each be answered from a single source."),
    Document(page_content="Relevance grading lets an LLM judge whether retrieved documents actually address the query before generation."),
    Document(page_content="Self-corrective retrieval rewrites and retries a query when the grader flags results as irrelevant."),
]

vectorstore = Chroma.from_documents(docs, OpenAIEmbeddings())
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})