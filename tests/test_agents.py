from datetime import datetime,timedelta,timezone
from app.agents import EquipmentSpecialist,BookingAgent,SupervisorAgent

def test_specialist_is_read_only():
    s=EquipmentSpecialist()
    assert set(s.tools.tools)=={"list_equipment","check_training","check_availability"}

def test_supervisor_inventory():
    r=SupervisorAgent().handle("show equipment")
    assert r["agent"]=="EquipmentSpecialist"
    assert len(r["equipment"])==4

def test_booking_agent():
    s=datetime.now(timezone.utc)+timedelta(days=8)
    e=s+timedelta(hours=2)
    r=BookingAgent().book("S1001","Arduino Kit",s,e,"A1")
    assert r["booking"]["result"]["booking_id"]=="A1"
