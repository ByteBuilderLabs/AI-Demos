import chromadb

client = chromadb.Client()
collection = client.get_or_create_collection(name="user_memory")

collection.add(
    documents=["Alice lives in London.", "Alice lives in Tokyo."],
    ids=["fact_1", "fact_2"],
)

result = collection.query(query_texts=["Where does Alice live?"], n_results=2)

for doc, dist in zip(result["documents"][0], result["distances"][0]):
    print(f"{doc}  (distance: {dist:.3f})")
