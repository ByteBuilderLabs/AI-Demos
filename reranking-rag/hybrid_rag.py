import os
from rank_bm25 import BM25Okapi
import chromadb
from chromadb.utils import embedding_functions
import cohere
from langchain_text_splitters import RecursiveCharacterTextSplitter

cohere_client = cohere.Client(os.environ["COHERE_API_KEY"])
chroma_client = chromadb.Client()
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


def load_and_chunk(path: str, chunk_size: int = 500, overlap: int = 50):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
    )
    return splitter.split_text(text)


chunks = load_and_chunk("docs/corpus.txt")


collection = chroma_client.create_collection(
    name="hybrid_docs", embedding_function=embed_fn
)
collection.add(
    documents=chunks,
    ids=[f"chunk_{i}" for i in range(len(chunks))],
)

tokenized = [c.lower().split() for c in chunks]
bm25 = BM25Okapi(tokenized)


def reciprocal_rank_fusion(rankings: list[list[int]], k: int = 60) -> list[int]:
    scores = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)


def hybrid_retrieve(query: str, top_k: int = 5, candidates: int = 50) -> list[str]:
    bm25_scores = bm25.get_scores(query.lower().split())
    bm25_top = sorted(range(len(bm25_scores)), key=lambda i: -bm25_scores[i])[
        :candidates
    ]

    vec_results = collection.query(query_texts=[query], n_results=candidates)
    vec_top = [int(i.split("_")[1]) for i in vec_results["ids"][0]]

    fused_ids = reciprocal_rank_fusion([bm25_top, vec_top])[:candidates]
    fused_docs = [chunks[i] for i in fused_ids]

    reranked = cohere_client.rerank(
        model="rerank-english-v3.0",
        query=query,
        documents=fused_docs,
        top_n=top_k,
    )
    return [fused_docs[r.index] for r in reranked.results]


if __name__ == "__main__":
    results = hybrid_retrieve("How to handle errors?")
    for i, chunk in enumerate(results, 1):
        print(f"\n--- Result {i} ---\n{chunk}")
