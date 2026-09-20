from contextlib import contextmanager
from app.db import get_conn

@contextmanager
def domain_conn():
    with get_conn() as conn:
        yield conn

def init_domain_db():
    with domain_conn() as conn, conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS equipment (
            equipment_id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS equipment_policy (
            equipment_id TEXT PRIMARY KEY REFERENCES equipment(equipment_id) ON DELETE CASCADE,
            training_required BOOLEAN NOT NULL DEFAULT FALSE,
            max_hours INTEGER NOT NULL CHECK (max_hours > 0)
        );
        CREATE TABLE IF NOT EXISTS training (
            student_id TEXT REFERENCES students(student_id) ON DELETE CASCADE,
            equipment_id TEXT REFERENCES equipment(equipment_id) ON DELETE CASCADE,
            PRIMARY KEY (student_id, equipment_id)
        );
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL REFERENCES students(student_id),
            equipment_id TEXT NOT NULL REFERENCES equipment(equipment_id),
            start_time TIMESTAMPTZ NOT NULL,
            end_time TIMESTAMPTZ NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            CHECK (end_time > start_time)
        );
        CREATE TABLE IF NOT EXISTS notifications (
            notification_id BIGSERIAL PRIMARY KEY,
            student_id TEXT NOT NULL REFERENCES students(student_id),
            message TEXT NOT NULL,
            idempotency_key TEXT NOT NULL UNIQUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_bookings_equipment_time
            ON bookings(equipment_id, start_time, end_time);
        CREATE INDEX IF NOT EXISTS idx_training_student
            ON training(student_id);
        """)

def seed_domain():
    with domain_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "TRUNCATE notifications, bookings, training, equipment_policy, equipment, students CASCADE"
        )
        cur.executemany(
            "INSERT INTO students(student_id,name) VALUES (%s,%s)",
            [("S1001","Arun"),("S1002","Bala"),("S1003","Charu")]
        )
        cur.executemany(
            "INSERT INTO equipment(equipment_id,name) VALUES (%s,%s)",
            [("EQ001","Arduino Kit"),("EQ002","Raspberry Pi Kit"),
             ("EQ003","Oscilloscope"),("EQ004","Logic Analyzer")]
        )
        cur.executemany(
            "INSERT INTO equipment_policy(equipment_id,training_required,max_hours) VALUES (%s,%s,%s)",
            [("EQ001",True,4),("EQ002",False,8),("EQ003",True,2),("EQ004",True,3)]
        )
        cur.executemany(
            "INSERT INTO training(student_id,equipment_id) VALUES (%s,%s)",
            [("S1001","EQ001"),("S1001","EQ002"),
             ("S1003","EQ003"),("S1003","EQ004")]
        )

def list_equipment():
    with domain_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT e.equipment_id, e.name, p.training_required, p.max_hours
            FROM equipment e JOIN equipment_policy p USING(equipment_id)
            ORDER BY e.equipment_id
        """)
        return cur.fetchall()

def get_equipment(equipment_name):
    with domain_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT e.equipment_id, e.name, p.training_required, p.max_hours
            FROM equipment e JOIN equipment_policy p USING(equipment_id)
            WHERE lower(e.name)=lower(%s)
        """, (equipment_name,))
        return cur.fetchone()

def has_training(student_id, equipment_id):
    with domain_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT EXISTS(SELECT 1 FROM training WHERE student_id=%s AND equipment_id=%s)",
            (student_id, equipment_id)
        )
        return bool(cur.fetchone()[0])

def is_available(equipment_id, start_time, end_time):
    with domain_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT NOT EXISTS(
                SELECT 1 FROM bookings
                WHERE equipment_id=%s AND status='active'
                  AND start_time < %s AND end_time > %s
            )
        """, (equipment_id, end_time, start_time))
        return bool(cur.fetchone()[0])

def create_booking(booking_id, student_id, equipment_id, start_time, end_time):
    with domain_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (equipment_id,))
        cur.execute(
            "SELECT training_required, max_hours FROM equipment_policy WHERE equipment_id=%s",
            (equipment_id,)
        )
        policy = cur.fetchone()
        if not policy:
            raise ValueError("Equipment not found.")

        training_required, max_hours = policy
        if (end_time - start_time).total_seconds() > max_hours * 3600:
            raise ValueError(f"Maximum booking duration is {max_hours} hours.")
        if training_required and not has_training(student_id, equipment_id):
            raise ValueError("Required training is not completed.")

        cur.execute("""
            SELECT 1 FROM bookings
            WHERE equipment_id=%s AND status='active'
              AND start_time < %s AND end_time > %s
            FOR UPDATE
        """, (equipment_id, end_time, start_time))
        if cur.fetchone():
            raise ValueError("Equipment is already booked for the requested time.")

        cur.execute("""
            INSERT INTO bookings
            (booking_id,student_id,equipment_id,start_time,end_time,status)
            VALUES (%s,%s,%s,%s,%s,'active')
            RETURNING booking_id
        """, (booking_id,student_id,equipment_id,start_time,end_time))
        return cur.fetchone()[0]

def return_booking(booking_id):
    with domain_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE bookings SET status='returned' WHERE booking_id=%s AND status='active' RETURNING booking_id",
            (booking_id,)
        )
        row = cur.fetchone()
        return row[0] if row else None

def notify(student_id, message, idem_key):
    with domain_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO notifications(student_id,message,idempotency_key)
            VALUES (%s,%s,%s)
            ON CONFLICT (idempotency_key) DO NOTHING
            RETURNING notification_id
        """, (student_id,message,idem_key))
        row = cur.fetchone()
        return row[0] if row else None
