from app.providers import ScriptedModel
from app.tools.lab_tools import make_dispatchers

class EquipmentSpecialist:
    def __init__(self):
        self.tools, _ = make_dispatchers()

    def inventory(self):
        return self.tools.call("list_equipment")

class BookingAgent:
    def __init__(self):
        _, self.tools = make_dispatchers()

    def book(self, student_id, equipment_name, start_time, end_time, booking_id):
        training = self.tools.call("check_training",student_id=student_id,equipment_name=equipment_name)
        if not training["ok"]:
            raise ValueError(training["message"])
        if training["training_required"] and not training["trained"]:
            raise ValueError("Student does not have the required training.")
        available = self.tools.call("check_availability",equipment_name=equipment_name,start_time=start_time,end_time=end_time)
        result = self.tools.call("book_equipment",student_id=student_id,equipment_name=equipment_name,start_time=start_time,end_time=end_time,booking_id=booking_id)
        self.tools.call("notify_student",student_id=student_id,message=f"Booking {booking_id} created for {equipment_name}.",idempotency_key=f"notification:{booking_id}")
        return {"training":training,"availability":available,"booking":result}

class SupervisorAgent:
    def __init__(self, model=None):
        self.model = model or ScriptedModel()
        self.specialist = EquipmentSpecialist()
        self.booking = BookingAgent()

    def handle(self,text,student_id="S1001",equipment_name="Arduino Kit",start_time=None,end_time=None,booking_id="B001"):
        decision = self.model.decide(text)
        if decision["intent"] == "inventory":
            return {"agent":"EquipmentSpecialist","equipment":self.specialist.inventory()}
        if decision["intent"] == "return":
            return {"agent":"BookingAgent","message":"Return flow requires a booking id."}
        if start_time is None or end_time is None:
            raise ValueError("start_time and end_time are required for booking.")
        return {"agent":"BookingAgent","result":self.booking.book(student_id,equipment_name,start_time,end_time,booking_id)}
