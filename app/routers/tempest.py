"""TIG · Tempest — the arcade game, served as a public Freehold page.

The game is one self-contained HTML file (canvas + JS, no backend), so it's
served raw via FileResponse — NOT through Jinja — so the templating engine never
touches the game's JavaScript braces. Mirrors the robot_panel pattern: a route
plus a page, linked from the nav. Public: no login required to play.
"""
from fastapi import APIRouter, Request
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/tempest")
async def tempest(request: Request):
    return FileResponse("static/tempest.html", media_type="text/html")
