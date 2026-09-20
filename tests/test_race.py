from datetime import datetime,timedelta,timezone
from app.tools.lab_tools import book_equipment
from app.lab_db import domain_conn

def test_same_booking_id_replay():
    s=datetime.now(timezone.utc)+timedelta(days=9)
    e=s+timedelta(hours=2)
    book_equipment("S1001","Arduino Kit",s,e,"RACE1")
    b=book_equipment("S1001","Arduino Kit",s,e,"RACE1")
    assert b["replayed"] is True

    with domain_conn() as conn,conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM bookings WHERE booking_id='RACE1'")
        assert cur.fetchone()[0]==1
