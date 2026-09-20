import json
import uuid
from app.db import get_conn

def enqueue(task):
    run_id = str(uuid.uuid4())
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO runs(run_id,task) VALUES (%s,%s)", (run_id,task))
    return run_id

def get_run(run_id):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT run_id,task,status,result_json,error FROM runs WHERE run_id=%s",
            (run_id,)
        )
        return cur.fetchone()

def add_message(run_id, role, content):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO messages(run_id,role,content) VALUES (%s,%s,%s)",
            (run_id,role,content)
        )

def save_result(run_id, result):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE runs SET status='completed',result_json=%s,updated_at=NOW() WHERE run_id=%s",
            (json.dumps(result, default=str),run_id)
        )

def save_failure(run_id, error):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE runs SET status='failed',error=%s,updated_at=NOW() WHERE run_id=%s",
            (str(error),run_id)
        )

def claim(worker_id, lease_seconds=10):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT run_id,task FROM runs
            WHERE status='queued'
            ORDER BY created_at
            FOR UPDATE SKIP LOCKED LIMIT 1
        """)
        row = cur.fetchone()
        if not row:
            return None
        run_id, task = row
        cur.execute(
            "UPDATE runs SET status='running',updated_at=NOW() WHERE run_id=%s",
            (run_id,)
        )
        cur.execute("""
            INSERT INTO leases(run_id,worker_id,expires_at)
            VALUES (%s,%s,NOW() + (%s * INTERVAL '1 second'))
            ON CONFLICT(run_id) DO UPDATE
            SET worker_id=EXCLUDED.worker_id,expires_at=EXCLUDED.expires_at
        """, (run_id,worker_id,lease_seconds))
        return {"run_id":run_id,"task":task}

def heartbeat(run_id, worker_id, lease_seconds=10):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            UPDATE leases
            SET expires_at=NOW() + (%s * INTERVAL '1 second')
            WHERE run_id=%s AND worker_id=%s
        """, (lease_seconds,run_id,worker_id))

def reap_expired():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            UPDATE runs r SET status='queued',updated_at=NOW()
            FROM leases l
            WHERE r.run_id=l.run_id AND l.expires_at < NOW()
            RETURNING r.run_id
        """)
        rows = cur.fetchall()
        cur.execute("DELETE FROM leases WHERE expires_at < NOW()")
        return [r[0] for r in rows]
