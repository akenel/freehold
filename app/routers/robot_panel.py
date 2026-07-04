"""Robot pack (Raspberry-Pi control): the panel, live SSE telemetry, RBAC-gated drive."""
import asyncio
import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse

import deps
import robot
from deps import templates

router = APIRouter()


def _can_drive(user) -> bool:
    return bool(user and "admin" in user.get("roles", []))


@router.get("/robot")
async def robot_panel(request: Request):
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("robot.html", {
        "request": request, "user": user, "can_drive": _can_drive(user),
    })


@router.get("/robot/stream")
async def robot_stream(request: Request):
    """Server-Sent Events — live telemetry streamed from the hardware bridge."""
    if not deps.current_user(request):
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    async def events():
        while True:
            if await request.is_disconnected():
                break
            try:
                payload = await robot.get_state()
            except Exception as exc:  # noqa: BLE001
                payload = {"error": str(exc)[:80]}
            yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(0.6)

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"})


@router.post("/robot/drive")
async def robot_drive(request: Request):
    """Only an operator (admin role) may send drive commands — RBAC on the wire."""
    user = deps.current_user(request)
    if not _can_drive(user):
        return JSONResponse({"error": "operator (admin) role required to drive"}, status_code=403)
    body = await request.json()
    return JSONResponse(await robot.drive(body.get("action", "stop"), body.get("speed", 0.5)))
