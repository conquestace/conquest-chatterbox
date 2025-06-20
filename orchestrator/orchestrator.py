import threading
import time
from collections import deque
from typing import Dict

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Backend(BaseModel):
    name: str
    base_url: str
    capabilities: list[str]
    max_queue: int = 5


backends: Dict[str, Backend] = {}
master_queue = deque()


class Job(BaseModel):
    type: str
    payload: dict
    preferred_backend: str | None = None


@app.post("/backends")
def register_backend(b: Backend):
    backends[b.name] = b
    return {"status": "ok"}


@app.post("/tts")
def tts_job(job: Job):
    job_id = job.payload.get("job_id")
    if not job_id:
        job.payload["job_id"] = str(len(master_queue) + 1)
    master_queue.append(job)
    return {"job_id": job.payload["job_id"]}


def scheduler_loop():
    while True:
        for name, b in list(backends.items()):
            try:
                r = httpx.get(f"{b.base_url}/queue")
                status = r.json()
            except Exception:
                continue
            capacity = b.max_queue - len(status.get("pending", [])) - len(status.get("running", []))
            while capacity > 0 and master_queue:
                job = master_queue.popleft()
                httpx.post(f"{b.base_url}/{job.type}", json=job.payload)
                capacity -= 1
        time.sleep(1)


threading.Thread(target=scheduler_loop, daemon=True).start()
