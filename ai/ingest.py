import os
import tempfile
from fastapi import UploadFile
import tiktoken
from pypdf import PdfReader
from .embeddings import get_embedding
from asyncpg import Connection

async def chunk(text: str, chunk_size: int = 1000, overlap: int = 200):
    enc = tiktoken.get_encoding('cl100k_base')
    tokens = enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = enc.decode(chunk_tokens)
        chunks.append(chunk_text)
        start += chunk_size - overlap
    return chunks

async def ingest_pdf(file: UploadFile, session_id: str, user_id: str, db_conn: Connection):
    contents = await file.read()
    original_filename = file.filename or "uploaded_file.pdf"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(original_filename)[1])
    tmp.write(contents)
    tmp.flush()
    file_path = tmp.name

    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

        chunks = await chunk(text)
        embeddings = [await get_embedding(chunk) for chunk in chunks]

        metadata_list = []
        for i, chunk in enumerate(chunks):
            metadata = {
                'source_filename': original_filename,
                'chunk_index': i,
                'total_chunks': len(chunks),
                'page_or_row': f"Page {i + 1}"
            }
            metadata_list.append(metadata)

            # Store chunk and embedding in the database
            await db_conn.execute(
                """
                INSERT INTO document_chunks (session_id, user_id, chunk_text, embedding, metadata)
                VALUES ($1, $2, $3, $4, $5)
                """,
                session_id, user_id, chunk, embeddings[i], metadata
            )
    finally:
        os.unlink(file_path)