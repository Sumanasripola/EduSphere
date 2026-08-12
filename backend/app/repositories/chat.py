import json
from app.db import get_conn, release_conn


def create_session(user_id: str, name: str = "New Chat"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_sessions (user_id, name) VALUES (%s, %s) RETURNING id, created_at;",
        (user_id, name),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    release_conn(conn)
    return {"id": str(row[0]), "name": name, "created_at": str(row[1])}


def list_sessions_for_user(user_id: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, created_at FROM chat_sessions WHERE user_id = %s ORDER BY created_at DESC;",
        (user_id,),
    )
    rows = cur.fetchall()
    cur.close()
    release_conn(conn)
    return [{"id": str(r[0]), "name": r[1], "created_at": str(r[2])} for r in rows]


def rename_session(session_id: str, name: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE chat_sessions SET name = %s WHERE id = %s;", (name, session_id))
    conn.commit()
    cur.close()
    release_conn(conn)


def session_belongs_to_user(session_id: str, user_id: str) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT count(*) FROM chat_sessions WHERE id = %s AND user_id = %s;",
        (session_id, user_id),
    )
    count = cur.fetchone()[0]
    cur.close()
    release_conn(conn)
    return count == 1


def add_message(session_id, role, text, citations=None, images=None, excel_path=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO messages (session_id, role, text, citations_json, images_json, excel_path)
           VALUES (%s, %s, %s, %s, %s, %s) RETURNING id, created_at;""",
        (
            session_id,
            role,
            text,
            json.dumps(citations) if citations is not None else None,
            json.dumps(images) if images is not None else None,
            excel_path,
        ),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    release_conn(conn)
    return {"id": str(row[0]), "created_at": str(row[1])}


def list_messages_for_session(session_id: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """SELECT id, role, text, citations_json, images_json, excel_path, created_at
           FROM messages WHERE session_id = %s ORDER BY created_at ASC;""",
        (session_id,),
    )
    rows = cur.fetchall()
    cur.close()
    release_conn(conn)
    return [
        {
            "id": str(r[0]),
            "role": r[1],
            "text": r[2],
            "citations": r[3],
            "images": r[4],
            "excel_path": r[5],
            "created_at": str(r[6]),
        }
        for r in rows
    ]
