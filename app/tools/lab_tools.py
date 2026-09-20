from app.idempotency import run_once
from app.lab_db import list_equipment as db_list_equipment, get_equipment, has_training, is_available, create_booking, return_booking, notify
from app.tools.dispatch import Tool, ToolDispatcher

def list_equipment():
    return db_list_equipment()

def check_training(student_id, equipment_name):
    equipment = get_equipment(equipment_name)
    if not equipment:
        return {"ok": False, "message": "Equipment not found."}
    return {
        "ok": True, "student_id": student_id, "equipment": equipment_name,
        "trained": has_training(student_id, equipment[0]),
        "training_required": equipment[2]
    }

def check_availability(equipment_name, start_time, end_time):
    equipment = get_equipment(equipment_name)
    if not equipment:
        return {"ok": False, "message": "Equipment not found."}
    return {
        "ok": True,
        "available": is_available(equipment[0], start_time, end_time),
        "equipment_id": equipment[0]
    }

def book_equipment(student_id, equipment_name, start_time, end_time, booking_id):
    equipment = get_equipment(equipment_name)
    if not equipment:
        raise ValueError("Equipment not found.")
    return run_once(
        f"booking:{booking_id}",
        "book_equipment",
        lambda: {
            "booking_id": create_booking(
                booking_id, student_id, equipment[0], start_time, end_time
            ),
            "student_id": student_id,
            "equipment": equipment_name
        }
    )

def return_equipment(booking_id):
    return {"booking_id": return_booking(booking_id), "returned": True}

def notify_student(student_id, message, idempotency_key):
    return {"notification_id": notify(student_id,message,idempotency_key), "sent": True}

def make_dispatchers():
    read_tools = ToolDispatcher([
        Tool("list_equipment","Read-only equipment listing.",list_equipment),
        Tool("check_training","Read-only training check.",check_training),
        Tool("check_availability","Read-only availability check.",check_availability),
    ])
    booking_tools = ToolDispatcher([
        Tool("list_equipment","Read-only equipment listing.",list_equipment),
        Tool("check_training","Read-only training check.",check_training),
        Tool("check_availability","Read-only availability check.",check_availability),
        Tool("book_equipment","Creates a booking; DB side effect; idempotent.",book_equipment,True),
        Tool("return_equipment","Returns a booking; DB side effect.",return_equipment,True),
        Tool("notify_student","Creates a notification; idempotent by key.",notify_student,True),
    ])
    return read_tools, booking_tools
