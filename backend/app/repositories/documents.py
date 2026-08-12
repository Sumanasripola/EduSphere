from app.db import get_conn, release_conn


def create_document(user_id: str, filename: str, doc_type: str, status: str = "processing"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO documents (user_id, filename, doc_type, status)
           VALUES (%s, %s, %s, %s) RETURNING id;""",
        (user_id, filename, doc_type, status),
    )
    doc_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    release_conn(conn)
    return str(doc_id)


def update_document_status(document_id: str, status: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE documents SET status = %s WHERE id = %s;", (status, document_id))
    conn.commit()
    cur.close()
    release_conn(conn)


def list_documents_for_user(user_id: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """SELECT id, filename, doc_type, status, uploaded_at
           FROM documents WHERE user_id = %s ORDER BY uploaded_at DESC;""",
        (user_id,),
    )
    rows = cur.fetchall()
    cur.close()
    release_conn(conn)
    return [
        {"id": str(r[0]), "filename": r[1], "doc_type": r[2], "status": r[3], "uploaded_at": str(r[4])}
        for r in rows
    ]


def user_owns_documents(user_id: str, document_ids: list) -> bool:
    """Verify every document_id in the list actually belongs to user_id."""
    if not document_ids:
        return True
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT count(*) FROM documents WHERE user_id = %s AND id = ANY(%s::uuid[]);",
        (user_id, document_ids),
    )
    count = cur.fetchone()[0]
    cur.close()
    release_conn(conn)
    return count == len(document_ids)
