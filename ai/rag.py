import os
from .embeddings import get_embedding
from asyncpg import Connection
import openai

async def retrieve_context(query: str, top_k: int, session_id: str, user_id: str, db_conn: Connection):
    query_embedding = await get_embedding(query)
    rows = await db_conn.fetch(
        """
        SELECT chunk_text, metadata
        FROM document_chunks
        WHERE session_id = $1 AND user_id = $2
        ORDER BY embedding <-> $3
        LIMIT $4
        """,
        session_id, user_id, query_embedding, top_k
    )
    return rows

async def answer_question(query: str, session_id: str, user_id: str, db_conn: Connection) -> dict:
    top_k = 5
    retrieved_chunks = await retrieve_context(query, top_k, session_id, user_id, db_conn)

    if not retrieved_chunks:
        return {"answer": "No relevant information found.", "sources": []}

    context = "\n".join([row['chunk_text'] for row in retrieved_chunks])
    sources = [{'filename': row['metadata']['source_filename'], 'location': row['metadata']['page_or_row']} for row in retrieved_chunks]

    prompt = f"Answer the following question based on the context provided:\n\nContext:\n{context}\n\nQuestion:\n{query}\n\nProvide a concise answer with citations."

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set.")

    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    answer = response.choices[0].message.content

    return {"answer": answer, "sources": sources}