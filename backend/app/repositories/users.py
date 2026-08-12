from app.db import get_conn, release_conn


def create_user(email: str, hashed_password: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (email, hashed_password) VALUES (%s, %s) RETURNING id, email;",
        (email, hashed_password),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    release_conn(conn)
    return {"id": str(row[0]), "email": row[1]}


def get_user_by_email(email: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, email, hashed_password FROM users WHERE email = %s;", (email,)
    )
    row = cur.fetchone()
    cur.close()
    release_conn(conn)
    if not row:
        return None
    return {"id": str(row[0]), "email": row[1], "hashed_password": row[2]}


def get_user_by_id(user_id: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, email FROM users WHERE id = %s;", (user_id,))
    row = cur.fetchone()
    cur.close()
    release_conn(conn)
    if not row:
        return None
    return {"id": str(row[0]), "email": row[1]}
