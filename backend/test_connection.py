from app.db import get_conn, release_conn

conn = get_conn()
cur = conn.cursor()
cur.execute("SELECT count(*) FROM users;")
print("Connected successfully! User count:", cur.fetchone()[0])
cur.close()
release_conn(conn)