import threading
import time
import random
import queue
import json
import os
from datetime import datetime

class Logger:
    def __init__(self, filename="system_log.json"):
        self.filename = filename
        self.lock = threading.Lock()
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as f:
                json.dump([], f)

    def log(self, data):
        with self.lock:
            with open(self.filename, "r+") as f:
                logs = json.load(f)
                logs.append(data)
                f.seek(0)
                json.dump(logs, f, indent=2)

class Database:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

    def update(self, key, value):
        with self.lock:
            self.data[key] = value

    def get_snapshot(self):
        with self.lock:
            return dict(self.data)

class Task:
    def __init__(self, name, complexity):
        self.name = name
        self.complexity = complexity
        self.status = "pending"
        self.result = None

    def execute(self):
        self.status = "running"
        work_time = random.uniform(1, 3) * self.complexity
        time.sleep(work_time)
        self.result = f"{self.name} result {random.randint(100,999)}"
        self.status = "done"
        return self.result

class Worker(threading.Thread):
    def __init__(self, name, task_queue, db, logger):
        super().__init__()
        self.name = name
        self.task_queue = task_queue
        self.db = db
        self.logger = logger

    def run(self):
        while True:
            try:
                task = self.task_queue.get(timeout=1)
            except queue.Empty:
                break
            start_time = datetime.now().isoformat()
            result = task.execute()
            end_time = datetime.now().isoformat()
            self.db.update(task.name, {"status": task.status, "result": result})
            self.logger.log({
                "worker": self.name,
                "task": task.name,
                "status": task.status,
                "result": result,
                "start": start_time,
                "end": end_time
            })
            self.task_queue.task_done()

class SystemMonitor(threading.Thread):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.running = True

    def run(self):
        while self.running:
            snapshot = self.db.get_snapshot()
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"🌀 Real-time Task Monitor — {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 60)
            for name, info in snapshot.items():
                print(f"{name:<15} | {info['status']:<10} | {info['result']}")
            time.sleep(1)

def main():
    db = Database()
    logger = Logger()
    task_queue = queue.Queue()
    tasks = [Task(f"Task-{i+1}", random.randint(1, 3)) for i in range(10)]
    for t in tasks:
        task_queue.put(t)
    workers = [Worker(f"Worker-{i+1}", task_queue, db, logger) for i in range(4)]
    for w in workers:
        w.start()
    monitor = SystemMonitor(db)
    monitor.start()
    for w in workers:
        w.join()
    monitor.running = False
    monitor.join()
    print("\n✅ Barcha vazifalar bajarildi. Log fayl: system_log.json")

if __name__ == "__main__":
    main()
