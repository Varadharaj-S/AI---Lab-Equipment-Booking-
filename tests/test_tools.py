from datetime import datetime,timedelta,timezone
from app.tools.lab_tools import list_equipment,check_training,check_availability,book_equipment

def test_list_equipment():
    assert len(list_equipment())==4

def test_training_true():
    assert check_training("S1001","Arduino Kit")["trained"] is True

def test_training_false():
    assert check_training("S1002","Arduino Kit")["trained"] is False

def test_availability_initial():
    s=datetime.now(timezone.utc)+timedelta(days=5)
    e=s+timedelta(hours=2)
    assert check_availability("Arduino Kit",s,e)["available"] is True

def test_booking_success():
    s=datetime.now(timezone.utc)+timedelta(days=6)
    e=s+timedelta(hours=2)
    r=book_equipment("S1001","Arduino Kit",s,e,"T1")
    assert r["result"]["booking_id"]=="T1"

def test_booking_idempotent():
    s=datetime.now(timezone.utc)+timedelta(days=7)
    e=s+timedelta(hours=2)
    a=book_equipment("S1001","Arduino Kit",s,e,"T2")
    b=book_equipment("S1001","Arduino Kit",s,e,"T2")
    assert a["replayed"] is False
    assert b["replayed"] is True
