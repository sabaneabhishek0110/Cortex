from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

# --- Load env variables ---
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# --- Upload clause as a node with category relationship ---
def insert_clause(tx, clause):
    tx.run("""
        MERGE (c:Clause {clause_id: $clause_id})
        SET c.text = $text, c.page = $page, c.source_doc = $source_doc

        MERGE (s:Source {name: $source_doc})
        MERGE (c)-[:FROM_SOURCE]->(s)
        
        FOREACH (cat IN [$category] |
            MERGE (catNode:Category {name: cat})
            MERGE (c)-[:CATEGORIZED_AS]->(catNode)
        )
        
        MATCH (a:Clause {{clause_id: $from}}), (b:Clause {{clause_id: $to}})
            MERGE (a)-[:{rel_type}]->(b)
    """, 
    clause_id=clause["clause_id"],
    text=clause["text"],
    page=clause["metadata"].get("page"),
    source_doc=clause["source_doc"],
    category=clause["metadata"].get("category", "Uncategorized"),
    )

# --- Bulk uploader ---
def upload_clauses_to_neo4j(clauses):
    with driver.session() as session:
        for clause in clauses:
            session.execute_write(insert_clause, clause)
        print("✅ All clauses uploaded to Neo4j.")

# --- Sample usage (if testing alone) ---
if __name__ == "__main__":
    clause_chunks = [
    {
        "clause_id": "Clause 1",
        "text": "Coverage begins 30 days after the policy start date.",
        "source_doc": "Policy2024.pdf",
        "metadata": {
            "page": 2,
            "category": "Coverage Start",
            "section": "Section A",
            "refers_to": [],
            "depends_on": []
        }
    },
    {
        "clause_id": "Clause 2",
        "text": "Pre-existing conditions are covered only after 12 months. Refer to Clause 1 for coverage timeline.",
        "source_doc": "Policy2024.pdf",
        "metadata": {
            "page": 3,
            "category": "Pre-Existing Conditions",
            "section": "Section A",
            "refers_to": ["Clause 1"],
            "depends_on": ["Clause 1"]
        }
    },
    {
        "clause_id": "Clause 3",
        "text": "Maternity coverage applies after 9 months. Subject to general coverage limits. Depends on Clause 1.",
        "source_doc": "Policy2024.pdf",
        "metadata": {
            "page": 4,
            "category": "Maternity",
            "section": "Section B",
            "refers_to": ["Clause 1"],
            "depends_on": ["Clause 1"]
        }
    },
    {
        "clause_id": "Clause 4",
        "text": "Newborn baby cover is valid only if maternity claim (Clause 3) was accepted.",
        "source_doc": "Policy2024.pdf",
        "metadata": {
            "page": 5,
            "category": "Maternity",
            "section": "Section B",
            "refers_to": ["Clause 3"],
            "depends_on": ["Clause 3"]
        }
    },
    {
        "clause_id": "Clause 5",
        "text": "Hospitalization due to accident is covered from day one. Refer to Clause 1 for all others.",
        "source_doc": "Policy2024.pdf",
        "metadata": {
            "page": 6,
            "category": "Emergency",
            "section": "Section A",
            "refers_to": ["Clause 1"],
            "depends_on": []
        }
    },
    {
        "clause_id": "Clause 6",
        "text": "Psychiatric treatment covered after 6 months, subject to pre-existing clause (Clause 2).",
        "source_doc": "Policy2024.pdf",
        "metadata": {
            "page": 7,
            "category": "Mental Health",
            "section": "Section C",
            "refers_to": ["Clause 2"],
            "depends_on": ["Clause 2"]
        }
    },
    {
        "clause_id": "Clause 7",
        "text": "Daycare procedures are allowed even if hospitalization criteria (Clause 1) is not met.",
        "source_doc": "Policy2024.pdf",
        "metadata": {
            "page": 8,
            "category": "Daycare",
            "section": "Section D",
            "refers_to": ["Clause 1"],
            "depends_on": []
        }
    },
    {
        "clause_id": "Clause 8",
        "text": "Cosmetic surgeries are excluded unless post-accident (see Clause 5).",
        "source_doc": "Policy2024.pdf",
        "metadata": {
            "page": 9,
            "category": "Exclusion",
            "section": "Section E",
            "refers_to": ["Clause 5"],
            "depends_on": ["Clause 5"]
        }
    }
]

    upload_clauses_to_neo4j(clause_chunks)
