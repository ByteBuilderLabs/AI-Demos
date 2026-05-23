import os
from dotenv import load_dotenv
from llama_parse import LlamaParse
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core import VectorStoreIndex

load_dotenv()

parser = LlamaParse(
    result_type="markdown",
    use_vendor_multimodal_model=True,
    vendor_multimodal_model_name="openai-gpt4o",
)


documents = parser.load_data("financial_report.pdf")
parsed_doc = documents[0]

print("--- Extracted Markdown ---")
print(parsed_doc.text[:500])


node_parser = MarkdownNodeParser()
nodes = node_parser.get_nodes_from_documents(documents)

print(f"Split into {len(nodes)} structural chunks.")


index = VectorStoreIndex(nodes)
query_engine = index.as_query_engine()

response = query_engine.query("What is the Q1 revenue in the table?")
print("--- ANSWER ---")
print(str(response))
