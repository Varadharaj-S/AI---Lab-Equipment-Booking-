import uuid
from app.agents import SupervisorAgent
from app.memory import claim, save_result, save_failure, heartbeat

class Worker:
    def __init__(self, worker_id=None):
        self.worker_id = worker_id or str(uuid.uuid4())
        self.agent = SupervisorAgent()

    def process_one(self):
        item = claim(self.worker_id)
        if not item:
            return None
        try:
            heartbeat(item["run_id"],self.worker_id)
            result = self.agent.handle(item["task"],booking_id="B-DEMO")
            save_result(item["run_id"],result)
            return result
        except Exception as exc:
            save_failure(item["run_id"],exc)
            raise
