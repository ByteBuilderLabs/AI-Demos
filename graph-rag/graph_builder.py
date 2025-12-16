import os
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain_neo4j import GraphCypherQAChain
from dotenv import load_dotenv
load_dotenv(override=True)


def build_graph_chain():
    # Connect to Neo4j
    graph = Neo4jGraph(
        url=os.environ["NEO4J_URI"],
        username=os.environ["NEO4J_USERNAME"],
        password=os.environ["NEO4J_PASSWORD"]
    )

    # Force a schema refresh to ensure the LLM sees current data structure
    graph.refresh_schema()
    print(graph.schema)

    return graph


def seed_database(graph):
    # Clear existing data (Be careful in prod!)
    graph.query("MATCH (n) DETACH DELETE n")

    # Create structured relationships
    query = """
    CREATE (p1:Project {name: "Project Apollo", status: "Active"})
    CREATE (p2:Project {name: "Project Hermes", status: "Delayed"})
    CREATE (m:Manager {name: "Alice"})
    CREATE (d:Dependency {name: "GPU Cluster"})

    MERGE (m)-[:MANAGES]->(p1)
    MERGE (m)-[:MANAGES]->(p2)
    MERGE (p1)-[:DEPENDS_ON]->(d)
    MERGE (p2)-[:DEPENDS_ON]->(d)
    """
    graph.query(query)
    print("Database seeded with relational data.")


def run_query(graph, question):
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    chain = GraphCypherQAChain.from_llm(
        llm=llm,
        graph=graph,
        verbose=True, # Essential for debugging generated Cypher
        allow_dangerous_requests=True 
    )

    response = chain.invoke({"query": question})
    return response

if __name__ == "__main__":
    graph_conn = build_graph_chain()
    seed_database(graph_conn)

    user_q = "Which manager has projects depending on the GPU Cluster?"
    result = run_query(graph_conn, user_q)

    print(f"\nFINAL ANSWER: {result['result']}")