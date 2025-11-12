from fastapi import FastAPI, Request, HTTPException
from db.query_tool import query_user_db, query_admin_db
import os
from dotenv import load_dotenv
import uvicorn
from fastapi.responses import FileResponse
from db.connection import get_connection


load_dotenv()
app = FastAPI(title="Supabase Company API")

ADMIN_KEY = os.getenv("ADMIN_API_KEY")
USER_KEY = os.getenv("USER_API_KEY")

@app.get("/openapi.yml")
async def get_openapi_spec():
    file_path = os.path.join(os.path.dirname(__file__), "openapi.yml")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="openapi.yml not found")
    return FileResponse(file_path, media_type="text/yaml")


def check_auth(request: Request, required_key: str, role_name: str):
    auth_header = request.headers.get("Authorization")
    if auth_header != f"Bearer {required_key}":
        raise HTTPException(status_code=403, detail=f"Invalid {role_name} API key")
    return role_name

@app.get("/schemas")
async def list_schemas(request: Request):
    """Return schemas and tables available to the authenticated role."""
    auth_header = request.headers.get("Authorization")

    if auth_header == f"Bearer {USER_KEY}":
        role = "user"
        allowed_schemas = ["company"]
    elif auth_header == f"Bearer {ADMIN_KEY}":
        role = "admin"
        allowed_schemas = ["company", "finance"]
    else:
        raise HTTPException(status_code=403, detail="Invalid API key")

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                schema_list = {}
                for schema in allowed_schemas:
                    cur.execute("""
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = %s
                        ORDER BY table_name;
                    """, (schema,))
                    tables = [r[0] for r in cur.fetchall()]
                    schema_list[schema] = tables

        return {"role": role, "schemas": schema_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/user/query")
async def user_query(request: Request):
    role = check_auth(request, USER_KEY, "user")
    data = await request.json()
    sql = data.get("sql")
    if not sql:
        raise HTTPException(status_code=400, detail="Missing SQL statement")

    try:
        results = query_user_db(sql)
        return {"status": "success", "rows": len(results), "results": results, "role": role}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/admin/query")
async def admin_query(request: Request):
    role = check_auth(request, ADMIN_KEY, "admin")
    data = await request.json()
    sql = data.get("sql")
    if not sql:
        raise HTTPException(status_code=400, detail="Missing SQL statement")

    try:
        results = query_admin_db(sql)
        return {"status": "success", "rows": len(results), "results": results, "role": role}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080)


