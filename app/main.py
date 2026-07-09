"""Freehold — app assembly.

Config + shared helpers live in deps.py; the routes live in routers/, grouped by
concern (base · door · loop · profile · extras · robot). This file just wires them
together — the app spine, kept small on purpose.
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

import deps
from routers import base, door, extras, loop, profile, robot_panel, tempest

app = FastAPI(title="Freehold", version="0.2.0-phase2")
# Signed, http-only session cookie. same_site=lax lets the OIDC redirect back in.
app.add_middleware(
    SessionMiddleware, secret_key=deps.SESSION_SECRET,
    same_site="lax", https_only=deps.SESSION_HTTPS_ONLY,
)
app.mount("/static", StaticFiles(directory="static"), name="static")

for _module in (base, door, loop, profile, extras, robot_panel, tempest):
    app.include_router(_module.router)


@app.exception_handler(404)
async def not_found(request: Request, exc):
    user = request.session.get("user") if "session" in request.scope else None
    return deps.templates.TemplateResponse("404.html", {"request": request, "user": user}, status_code=404)
