# import os
# import re
# import json
# import requests
# from openai import OpenAI
# from dotenv import load_dotenv
# from datetime import datetime

# load_dotenv()

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# BACKEND_URL = os.getenv("BACKEND_URL", "https://e7f4f5645351.ngrok-free.app")
# USER_KEY = os.getenv("USER_API_KEY")
# ADMIN_KEY = os.getenv("ADMIN_API_KEY")
# LOG_FILE = "query_log.json"

# def detect_role(prompt: str) -> str:
#     text = prompt.lower()
#     admin_keywords = [
#         "finance", "financial", "transaction", "transactions",
#         "budget", "budgets", "expense", "expenses", "revenue", "profit", "loss",
#         "balance sheet", "cost", "income", "accounting",
#         "schema", "schemas", "database structure", "tables",
#         "admin", "audit"
#     ]
#     return "admin" if any(word in text for word in admin_keywords) else "user"

# def log_query(prompt, sql, role, result):
#     entry = {
#         "timestamp": datetime.utcnow().isoformat(),
#         "prompt": prompt,
#         "sql": sql,
#         "role": role,
#         "result": result,
#     }
#     try:
#         logs = json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else []
#         logs.append(entry)
#         json.dump(logs, open(LOG_FILE, "w"), indent=2)
#     except Exception:
#         pass

# def fetch_schemas_from_backend(role: str):
#     endpoint = "/schemas"
#     url = f"{BACKEND_URL}{endpoint}"
#     headers = {
#         "Authorization": f"Bearer {USER_KEY if role == 'user' else ADMIN_KEY}"
#     }
#     try:
#         resp = requests.get(url, headers=headers, timeout=20)
#         resp.raise_for_status()
#         data = resp.json()
#         schemas = data.get("schemas", {})
#         schema_text = []
#         for schema, tables in schemas.items():
#             table_list = ", ".join(tables)
#             schema_text.append(f"{schema} schema – tables: {table_list}")
#         return "\n".join(schema_text)
#     except Exception as e:
#         print(f"Error fetching schemas: {e}")
#         return "company.employees"

# def call_backend(sql: str, role: str, prompt: str):
#     endpoint = "/user/query" if role == "user" else "/admin/query"
#     url = f"{BACKEND_URL}{endpoint}"
#     headers = {
#         "Authorization": f"Bearer {USER_KEY if role == 'user' else ADMIN_KEY}",
#         "Content-Type": "application/json",
#     }
#     try:
#         resp = requests.post(url, json={"sql": sql}, headers=headers, timeout=30)
#         if not resp.ok:
#             print(f"Backend {resp.status_code}: {resp.text}")
#         resp.raise_for_status()
#         data = resp.json()
#         print("\nBackend response:\n", data)
#         if "results" in data and isinstance(data["results"], list):
#             print(f"\nSummary: Retrieved {len(data['results'])} rows.")
#         else:
#             print("\nNo data found or invalid response structure.")
#         log_query(prompt, sql, role, data)
#     except requests.exceptions.RequestException as e:
#         print(f"Backend error: {e}")
#         log_query(prompt, sql, role, str(e))

# def run_assistant(prompt: str):
#     print(f"Sending prompt to assistant: {prompt}")
#     role = detect_role(prompt)
#     print(f"Detected role: {role}")
#     allowed_schemas = fetch_schemas_from_backend(role)
#     sql_instructions = (
#         f"You are an expert SQL assistant for a PostgreSQL database.\n"
#         f"The current user has access to the following schemas and tables:\n\n{allowed_schemas}\n\n"
#         "Generate a valid SQL SELECT query that answers the user's question.\n"
#         "Rules:\n"
#         "- Always prefix tables with their schema name (e.g., company.employees)\n"
#         "- Only use tables listed above.\n"
#         "- Output ONLY the SQL query — no markdown, no explanations.\n"
#         "- Do not use INSERT, UPDATE, DELETE, or non-SELECT statements."
#     )
#     try:
#         response = client.responses.create(
#             model="gpt-4o",
#             input=[
#                 {"role": "system", "content": sql_instructions},
#                 {"role": "user", "content": prompt},
#             ],
#         )
#         sql = (response.output_text or "").strip()
#         if "```" in sql:
#             sql = sql.replace("```sql", "").replace("```", "").strip()
#         match = re.search(r"(?i)(select\s.+)", sql, re.DOTALL)
#         if match:
#             sql = match.group(1).strip()
#         if not sql.lower().startswith("select"):
#             print("Model did not return SQL:\n", sql)
#             log_query(prompt, sql, role, "No valid SQL generated")
#             return
#         print(f"Generated SQL: {sql}")
#         call_backend(sql, role, prompt)
#     except Exception as e:
#         print(f"Error generating SQL: {e}")
#         log_query(prompt, "N/A", role, f"Error: {e}")

# if __name__ == "__main__":
#     user_prompt = input("Enter your question: ")
#     run_assistant(user_prompt)




import os
import re
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
BACKEND_URL = os.getenv("BACKEND_URL", "https://e7f4f5645351.ngrok-free.app")
USER_KEY = os.getenv("USER_API_KEY")
ADMIN_KEY = os.getenv("ADMIN_API_KEY")
LOG_FILE = "query_log.json"

def detect_role(prompt: str) -> str:
    text = prompt.lower()
    admin_keywords = [
        "finance", "financial", "transaction", "transactions",
        "budget", "budgets", "expense", "expenses", "revenue",
        "profit", "loss", "balance sheet", "cost", "income",
        "accounting", "schema", "schemas", "database structure",
        "tables", "admin", "audit"
    ]
    return "admin" if any(word in text for word in admin_keywords) else "user"

def log_query(prompt, sql, role, result):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "prompt": prompt,
        "sql": sql,
        "role": role,
        "result": result,
    }
    try:
        logs = json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else []
        logs.append(entry)
        json.dump(logs, open(LOG_FILE, "w"), indent=2)
    except Exception as e:
        print(f"Logging error: {e}")

def fetch_schemas_from_backend(role: str) -> str:
    endpoint = "/schemas"
    url = f"{BACKEND_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {USER_KEY if role == 'user' else ADMIN_KEY}"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        schemas = data.get("schemas", {})
        schema_text = []
        for schema, tables in schemas.items():
            table_list = ", ".join(tables)
            schema_text.append(f"{schema} schema – tables: {table_list}")
        return "\n".join(schema_text)
    except Exception as e:
        print(f"Error fetching schemas: {e}")
        return "company.employees"

def call_backend(sql: str, role: str, prompt: str):
    endpoint = "/user/query" if role == "user" else "/admin/query"
    url = f"{BACKEND_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {USER_KEY if role == 'user' else ADMIN_KEY}",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(url, json={"sql": sql}, headers=headers, timeout=30)
        if not resp.ok:
            print(f"Backend {resp.status_code}: {resp.text}")
        resp.raise_for_status()
        data = resp.json()
        print("\nBackend response:\n", json.dumps(data, indent=2))
        if "results" in data and isinstance(data["results"], list):
            print(f"\nSummary: Retrieved {len(data['results'])} rows.")
        else:
            print("\nNo data found or invalid response structure.")
        log_query(prompt, sql, role, data)
    except requests.exceptions.RequestException as e:
        print(f"Backend error: {e}")
        log_query(prompt, sql, role, str(e))

def run_assistant(prompt: str):
    print(f"Sending prompt to assistant: {prompt}")
    role = detect_role(prompt)
    print(f"Detected role: {role}")
    allowed_schemas = fetch_schemas_from_backend(role)
    sql_instructions = (
        f"You are an expert SQL assistant for a PostgreSQL database.\n"
        f"The current user has access to the following schemas and tables:\n\n{allowed_schemas}\n\n"
        "Generate a valid SQL SELECT query that answers the user's question.\n"
        "Rules:\n"
        "- Always prefix tables with their schema name (e.g., company.employees)\n"
        "- Only use tables listed above.\n"
        "- Output ONLY the SQL query — no markdown, no explanations.\n"
        "- Do not use INSERT, UPDATE, DELETE, or non-SELECT statements."
    )
    try:
        response = client.responses.create(
            model="gpt-4o",
            input=[
                {"role": "system", "content": sql_instructions},
                {"role": "user", "content": prompt},
            ],
        )
        sql = (response.output_text or "").strip()
        if "```" in sql:
            sql = sql.replace("```sql", "").replace("```", "").strip()
        match = re.search(r"(?i)(select\s.+)", sql, re.DOTALL)
        if match:
            sql = match.group(1).strip()
        if not sql.lower().startswith("select"):
            print("Model did not return valid SQL:\n", sql)
            log_query(prompt, sql, role, "No valid SQL generated")
            return
        print(f"Generated SQL: {sql}")
        call_backend(sql, role, prompt)
    except Exception as e:
        print(f"Error generating SQL: {e}")
        log_query(prompt, "N/A", role, f"Error: {e}")

if __name__ == "__main__":
    user_prompt = input("Enter your question: ").strip()
    if not user_prompt:
        print("No question provided. Exiting.")
    else:
        run_assistant(user_prompt)
