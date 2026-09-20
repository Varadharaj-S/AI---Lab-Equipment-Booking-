from datetime import datetime,timedelta,timezone
from app.db import init_agent_db
from app.lab_db import init_domain_db,seed_domain
from app.memory import enqueue,get_run
from app.agents import SupervisorAgent

init_agent_db()
init_domain_db()
seed_domain()

start=datetime.now(timezone.utc)+timedelta(days=1)
end=start+timedelta(hours=3)
run_id=enqueue("Book Arduino Kit")

result=SupervisorAgent().handle(
    "Book Arduino Kit",student_id="S1001",
    equipment_name="Arduino Kit",start_time=start,
    end_time=end,booking_id="B-DEMO"
)

print("Run:",run_id)
print("Result:",result)
print("Stored run:",get_run(run_id))
