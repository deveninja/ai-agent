import csv
import io
import os
from itertools import zip_longest
from uuid import uuid4

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

from db.chroma_client import client

collection = client.get_or_create_collection("knowledge")
model = SentenceTransformer("all-MiniLM-L6-v2")


def chunk_text(text, size=500):
    chunks = []

    for i in range(0, len(text), size):
        chunks.append(text[i:i + size])

    return chunks


def extract_text_from_pdf(file_bytes):
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()

        if text:
            pages.append(f"Page {page_number}\n{text}")

    return "\n\n".join(pages)


def extract_text_from_csv(file_bytes):
    try:
        decoded = file_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        decoded = file_bytes.decode("latin-1")

    rows = list(csv.reader(io.StringIO(decoded)))

    if not rows:
        return ""

    if len(rows) == 1:
        return ", ".join(rows[0])

    headers = rows[0]
    lines = []

    for row_number, row in enumerate(rows[1:], start=1):
        pairs = []

        for header, value in zip_longest(headers, row, fillvalue=""):
            header_clean = header.strip() if isinstance(header, str) else ""
            value_clean = value.strip() if isinstance(value, str) else ""
            pairs.append(f"{header_clean}: {value_clean}")

        lines.append(f"Row {row_number} | " + " | ".join(pairs))

    return "\n".join(lines)


def extract_text_from_file(file_name, file_bytes):
    extension = os.path.splitext(file_name.lower())[1]

    if extension == ".pdf":
        return extract_text_from_pdf(file_bytes)

    if extension == ".csv":
        return extract_text_from_csv(file_bytes)

    raise ValueError("Only PDF and CSV files are supported.")


def index_uploaded_file(uploaded_file):
    file_bytes = uploaded_file.getvalue()

    if not file_bytes:
        raise ValueError("The uploaded file is empty.")

    text = extract_text_from_file(uploaded_file.name, file_bytes)

    if not text.strip():
        raise ValueError("No readable text was found in this file.")

    docs = chunk_text(text)
    embeddings = model.encode(docs).tolist()

    ids = [str(uuid4()) for _ in docs]
    metadatas = [
        {
            "source": uploaded_file.name,
            "chunk_index": index
        }
        for index, _ in enumerate(docs)
    ]

    collection.add(
        documents=docs,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )

    return {
        "file_name": uploaded_file.name,
        "chunks_indexed": len(docs)
    }
