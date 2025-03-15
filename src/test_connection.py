from db import get_db_connection

def test_database_connection():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        result = cur.fetchone()
        assert result[0] == 1
    finally:
        if conn:
            conn.close()
