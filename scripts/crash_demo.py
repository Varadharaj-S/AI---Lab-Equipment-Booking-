from datetime import datetime,timedelta,timezone
from app.db import init_agent_db
from app.lab_db import init_domain_db,seed_domain,domain_conn
from app.tools.lab_tools import book_equipment

init_agent_db()
init_domain_db()
seed_domain()

start=datetime.now(timezone.utc)+timedelta(days=2)
end=start+timedelta(hours=2)

first=book_equipment("S1001","Arduino Kit",start,end,"B-CRASH")
print("Worker 1 created booking:",first)

second=book_equipment("S1001","Arduino Kit",start,end,"B-CRASH")
print("Worker 2 replay result:",second)

with domain_conn() as conn,conn.cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM bookings WHERE booking_id='B-CRASH'")
    count=cur.fetchone()[0]

print("Bookings after replay:",count)
assert count==1
assert second["replayed"] is True
print("PASS: crash replay did not duplicate the booking.")
