from app.db import get_conn, release_conn


def add_chunks(document_id: str, user_id: str, chunks_with_metadata: list, embeddings) -> int:
    """
    chunks_with_metadata: list of dicts like {"text": ..., "page": ..., "location": ...}
    embeddings: list/array of vectors, same length and order as chunks_with_metadata
    """
    conn = get_conn()
    cur = conn.cursor()
    for chunk, vec in zip(chunks_with_metadata, embeddings):
        cur.execute(
            """INSERT INTO chunks (document_id, user_id, chunk_text, page, location, embedding)
               VALUES (%s, %s, %s, %s, %s, %s);""",
            (document_id, user_id, chunk["text"], chunk.get("page"), chunk.get("location"), vec),
        )
    conn.commit()
    count = len(chunks_with_metadata)
    cur.close()
    release_conn(conn)
    return count


def search(query_vector, user_id: str, document_ids: list = None, k: int = 20):
    """
    Returns nearest chunks scoped to user_id, optionally further scoped to
    a specific set of document_ids.
    """
    conn = get_conn()
    cur = conn.cursor()

    if document_ids:
        cur.execute(
            """
            SELECT c.chunk_text, c.page, c.location, c.document_id, d.filename
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE c.user_id = %s AND c.document_id = ANY(%s::uuid[])
            ORDER BY c.embedding <-> %s
            LIMIT %s;
            """,
            (user_id, document_ids, query_vector, k),
        )
    else:
        cur.execute(
            """
            SELECT c.chunk_text, c.page, c.location, c.document_id, d.filename
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE c.user_id = %s
            ORDER BY c.embedding <-> %s
            LIMIT %s;
            """,
            (user_id, query_vector, k),
        )

    rows = cur.fetchall()
    cur.close()
    release_conn(conn)
    return [
        {"text": r[0], "page": r[1], "location": r[2], "document_id": str(r[3]), "source": r[4]}
        for r in rows
    ]
