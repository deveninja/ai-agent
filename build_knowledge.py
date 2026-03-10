import os
from db.chroma_client import client

from sentence_transformers import SentenceTransformer

collection = client.get_or_create_collection("knowledge")

model = SentenceTransformer("all-MiniLM-L6-v2")

docs = []
ids = []

folder = "knowledge"


def chunk_text(text, size=500):

    chunks = []

    for i in range(0, len(text), size):
        chunks.append(text[i:i+size])

    return chunks

for i, file in enumerate(os.listdir(folder)):
    
    with open(f"{folder}/{file}", "r", encoding="utf-8") as f:
        text = f.read()

    for chunk in chunk_text(text):
        docs.append(chunk)
        ids.append(str(len(ids)))

embeddings = model.encode(docs).tolist()

print("Docs being added:", len(docs))

collection.add(
    documents=docs,
    embeddings=embeddings,
    ids=ids
)

print("Knowledge base built.")
