"""robot-sim — a stand-in for the real hardware bridge.

This fakes a little robot: it holds a pose (x, y, heading), fakes sensors
(ultrasonic distance, temperature, battery), and accepts drive commands. It
speaks plain REST — GET /state, POST /drive — so the Freehold app talks to it
exactly the way it will talk to a real Raspberry Pi bridge later. Swap this
container for one that reads real GPIO, keep the same two endpoints, done.
"""
import asyncio
import math
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

START = time.time()
state = {
    "x": 0.0, "y": 0.0, "heading": 90.0, "speed": 0.0,
    "distance_cm": 80.0, "temp_c": 24.5, "battery": 100.0, "cmd": "stop",
}
STEP = 0.6


async def _tick():
    while True:
        cmd = state["cmd"]
        if cmd == "forward":
            state["speed"] = 0.6
            state["x"] += math.cos(math.radians(state["heading"])) * STEP
            state["y"] += math.sin(math.radians(state["heading"])) * STEP
        elif cmd == "back":
            state["speed"] = -0.4
            state["x"] -= math.cos(math.radians(state["heading"])) * STEP * 0.6
            state["y"] -= math.sin(math.radians(state["heading"])) * STEP * 0.6
        elif cmd == "left":
            state["heading"] = (state["heading"] + 12) % 360
            state["speed"] = 0.0
        elif cmd == "right":
            state["heading"] = (state["heading"] - 12) % 360
            state["speed"] = 0.0
        else:
            state["speed"] = 0.0
        now = time.time()
        state["distance_cm"] = round(max(4.0, 60 + 45 * math.sin(now / 2.5)), 1)
        state["temp_c"] = round(24 + 2.2 * math.sin(now / 12), 1)
        state["battery"] = round(max(0.0, 100 - (now - START) * 0.15), 1)
        await asyncio.sleep(0.4)


@asynccontextmanager
async def lifespan(app):
    task = asyncio.create_task(_tick())
    yield
    task.cancel()


app = FastAPI(title="robot-sim", lifespan=lifespan)


class Cmd(BaseModel):
    action: str = "stop"
    speed: float = 0.5


@app.get("/state")
async def get_state():
    return {**state, "x": round(state["x"], 1), "y": round(state["y"], 1),
            "heading": round(state["heading"], 1)}


@app.post("/drive")
async def drive(cmd: Cmd):
    if cmd.action in ("forward", "back", "left", "right", "stop"):
        state["cmd"] = cmd.action
    return {"ok": True, "cmd": state["cmd"]}


@app.get("/healthz")
async def healthz():
    return {"status": "ok", "robot": "sim"}
