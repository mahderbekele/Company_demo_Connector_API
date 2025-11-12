from db.connection import get_connection

def query_user_db(sql: str) -> list[dict]:
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith("SELECT"):
        raise ValueError("Only SELECT statements are allowed.")
    lower_sql = sql.lower()
    if not ("company." in lower_sql or "information_schema." in lower_sql):
        raise ValueError("Only queries on the 'company' or 'information_schema' schemas are permitted.")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            columns = [desc[0] for desc in cur.description]
            rows = [dict(zip(columns, row)) for row in cur.fetchall()]
    return rows

def query_admin_db(sql: str) -> list[dict]:
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith("SELECT"):
        raise ValueError("Only SELECT statements are allowed.")
    lower_sql = sql.lower()
    if not ("company." in lower_sql or "finance." in lower_sql or "information_schema." in lower_sql):
        raise ValueError("Admins may only query 'company', 'finance', or 'information_schema' schemas.")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            columns = [desc[0] for desc in cur.description]
            rows = [dict(zip(columns, row)) for row in cur.fetchall()]
    return rows
