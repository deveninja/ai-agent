"""
memory.py

Provides persistent vector memory for the AI agent using ChromaDB.
Conversation snippets are embedded and stored, then retrieved via
semantic similarity search to give the agent contextual recall.
"""

import uuid
from db.chroma_client import client


# ChromaDB collection used to store and query conversation memories
collection = client.get_or_create_collection("memory")


def save_memory(text):
    """
    Persist a piece of text into the vector memory store.

    Embeds the provided text and stores it in the ChromaDB collection
    with a randomly generated UUID as its unique identifier.

    Args:
        text (str): The conversation snippet or fact to remember.
    """

    collection.add(
        documents=[text],
        ids=[str(uuid.uuid4())]
    )


def search_memory(query):
    """
    Retrieve stored memories that are semantically similar to the query.

    Queries the ChromaDB collection for the top 3 closest matches and
    filters out results whose distance exceeds the relevance threshold
    (1.2), keeping only contextually meaningful memories.

    Args:
        query (str): The search string used to find relevant memories.

    Returns:
        list[str]: A list of relevant memory documents (may be empty).
    """

    results = collection.query(
        query_texts=[query],
        n_results=3
    )

    docs = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]

    memory = []

    for doc, distance in zip(docs, distances):

        # Only keep relevant memories (distance < 1.2 means high similarity)
        if distance < 1.2:
            memory.append(doc)

    return memory