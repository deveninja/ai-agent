"""
knowledge_search.py

Provides semantic search over the company knowledge base stored in ChromaDB.
Documents (e.g. company info, services) are embedded at build time and can
be retrieved here by semantic similarity to answer agent queries.
"""

from db.chroma_client import client

# ChromaDB collection that holds company knowledge documents
collection = client.get_or_create_collection("knowledge")


def search_knowledge(query):
    """
    Find knowledge-base documents most relevant to the given query.

    Queries the ChromaDB knowledge collection for the top 3 closest
    matches and filters out results whose distance exceeds 1.2,
    keeping only semantically relevant documents.

    Args:
        query (str): A natural-language question or search phrase.

    Returns:
        list[str]: A list of matching document strings (may be empty).
    """

    results = collection.query(
        query_texts=[query],
        n_results=3
    )

    docs = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]

    knowledge = []

    for doc, distance in zip(docs, distances):

        print("DOC:", doc)
        print("DISTANCE:", distance)

        # Lower distance = higher similarity; 1.2 is the relevance threshold
        if distance < 1.2:
            knowledge.append(doc)

    return knowledge