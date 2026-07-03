"""Freehold — client for the robot hardware bridge (REST).

The app never knows whether it's talking to the simulator or a real Raspberry Pi
— it only knows the REST contract (GET /state, POST /drive). Point ROBOT_URL at
whichever, and nothing else changes.
"""
import os

import httpx

ROBOT_URL = os.getenv("ROBOT_URL", "http://robot-sim:9100").rstrip("/")


async def get_state() -> dict:
    async with httpx.AsyncClient(timeout=3) as client:
        resp = await client.get(f"{ROBOT_URL}/state")
        resp.raise_for_status()
        return resp.json()


async def drive(action: str, speed: float = 0.5) -> dict:
    async with httpx.AsyncClient(timeout=3) as client:
        resp = await client.post(f"{ROBOT_URL}/drive", json={"action": action, "speed": speed})
        resp.raise_for_status()
        return resp.json()
