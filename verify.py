from db.chroma_client import client

collection = client.get_collection("knowledge")

print("Document count:", collection.count())