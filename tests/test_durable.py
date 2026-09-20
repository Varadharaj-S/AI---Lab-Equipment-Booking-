from app.memory import enqueue,claim,heartbeat,reap_expired,get_run

def test_enqueue_and_claim():
    rid=enqueue("test task")
    item=claim("worker-a")
    assert item["run_id"]==rid

def test_get_run():
    rid=enqueue("another task")
    assert get_run(rid)[0]==rid

def test_heartbeat():
    rid=enqueue("heartbeat task")
    item=claim("worker-b")
    heartbeat(rid,"worker-b")
    assert item["run_id"]==rid

def test_reap_returns_list():
    assert isinstance(reap_expired(),list)
