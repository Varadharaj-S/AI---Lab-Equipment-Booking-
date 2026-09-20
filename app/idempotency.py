import json
from app.db import get_conn

def run_once(key, operation, fn):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT result_json FROM idempotency_keys WHERE key=%s FOR UPDATE",
            (key,)
        )
        existing = cur.fetchone()
        if existing:
            return {"replayed": True, "result": json.loads(existing[0])}

        result = fn()
        cur.execute(
            "INSERT INTO idempotency_keys(key,operation,result_json) VALUES (%s,%s,%s)",
            (key,operation,json.dumps(result, default=str))
        )
        return {"replayed": False, "result": result}
