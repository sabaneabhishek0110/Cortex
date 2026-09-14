from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
from queryExtractor import extract_info

# --- Load Neo4j credentials ---
load_dotenv()
uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(uri, auth=(user, password))

# --- Query the graph using structured query data ---
def get_clauses_from_graph(query_data):
    clause_results = []

    with driver.session() as session:
        cypher = """
        MATCH (c:Clause)-[:CATEGORIZED_AS]->(cat:Category)
        WHERE toLower(cat.name) CONTAINS toLower($category)
        RETURN c.clause_id AS clause_id, c.text AS text, c.source_doc AS doc, c.page AS page
        LIMIT 5
        """

        # Fallback to category/procedure
        category = query_data.get("procedure") or query_data.get("relation") or "general"

        results = session.run(cypher, category=category)
        for record in results:
            clause_results.append({
                "clause_id": record["clause_id"],
                "text": record["text"],
                "source_doc": record["doc"],
                "page": record["page"]
            })

    return clause_results

# --- Entry point ---
if __name__ == "__main__":
    query = input("🧠 Enter your insurance query: ")
    structured = extract_info(query)
    print("\n🔍 Extracted Info:", structured)

    clauses = get_clauses_from_graph(structured)

    print(f"\n📄 Top {len(clauses)} matching clauses from GraphDB:\n")
    for i, c in enumerate(clauses):
        print(clauses)
