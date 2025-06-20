import uuid
import threading
import time
import json
import asyncio
from collections import deque

from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from starlette.websockets import WebSocketDisconnect

from chatterbox.tts import ChatterboxTTS


app = FastAPI()
queue = deque()
running = {}
history = {}

# Load TTS model on startup
tts_model = ChatterboxTTS.from_pretrained("cuda")


class TTSReq(BaseModel):
    text: str
    params: dict = {}


@app.post("/tts")
def tts(req: TTSReq):
    job_id = str(uuid.uuid4())
    queue.append(("tts", job_id, req))
    return {"job_id": job_id}


@app.websocket("/ws/{job_id}")
async def ws_stream(ws: WebSocket, job_id: str):
    await ws.accept()
    try:
        while True:
            if job_id in history:
                await ws.send_json({"status": "done", **history[job_id]})
                break
            if job_id in running:
                await ws.send_json({"status": "running", "progress": running[job_id]})
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass


@app.get("/queue")
def queue_status():
    return {
        "running": list(running.keys()),
        "pending": [job_id for _, job_id, _ in list(queue)],
    }


@app.delete("/queue/{job_id}")
def cancel(job_id: str):
    global queue
    queue = deque([item for item in queue if item[1] != job_id])
    return {"status": "cancelled"}


@app.get("/history")
def get_history():
    return history


def worker_loop():
    while True:
        if not queue:
            time.sleep(0.05)
            continue
        task, job_id, payload = queue.popleft()
        running[job_id] = 0.0
        if task == "tts":
            # Fake progress updates while generating
            for step in range(10):
                running[job_id] = step / 10
                time.sleep(0.2)
            wav = tts_model.generate(payload.text, **payload.params)
            path = f"/tmp/{job_id}.wav"
            # Save wav to path
            import torchaudio as ta
            ta.save(path, wav, tts_model.sr)
            history[job_id] = {"url": path}
        running.pop(job_id, None)


threading.Thread(target=worker_loop, daemon=True).start()
