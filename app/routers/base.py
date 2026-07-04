"""Public + base pages: home, health/version, PWA worker, manifesto, legal, i18n."""
from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

import build_info
import deps
import i18n
from deps import APP_ENV, KC_PUBLIC_URL, KC_REALM, templates

router = APIRouter()


@router.get("/healthz")
async def healthz():
    ok, _ = await deps.db_check()
    return JSONResponse({"status": "ok", "env": APP_ENV, "realm": KC_REALM, "db": ok})


@router.get("/sw.js")
async def service_worker():
    """Served from root so the service worker's scope is the whole app (PWA)."""
    return FileResponse("static/sw.js", media_type="application/javascript")


@router.get("/version")
async def version():
    """The truthful build bar — what the deploy stamps, this serves, parity checks."""
    return JSONResponse({
        "version": build_info.version(), "sha": build_info.sha(),
        "date": build_info.date(), "env": APP_ENV,
    })


@router.get("/")
async def index(request: Request):
    ok, message = await deps.db_check()
    return templates.TemplateResponse("index.html", {
        "request": request, "env": APP_ENV, "realm": KC_REALM, "kc_url": KC_PUBLIC_URL,
        "db_ok": ok, "db_msg": message, "user": deps.current_user(request),
        "build": {"version": build_info.version(), "sha": build_info.sha(), "date": build_info.date()},
    })


@router.get("/manifesto")
async def manifesto(request: Request):
    return templates.TemplateResponse("manifesto.html", {"request": request, "user": deps.current_user(request)})


@router.get("/sitemap")
async def sitemap(request: Request):
    """A human site map — everything the app does, one honest page."""
    return templates.TemplateResponse("sitemap.html", {"request": request, "user": deps.current_user(request)})


@router.get("/terms")
async def terms(request: Request):
    return templates.TemplateResponse("terms.html", {"request": request, "user": deps.current_user(request)})


@router.get("/privacy")
async def privacy(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request, "user": deps.current_user(request)})


@router.get("/lang/{code}")
async def set_lang(request: Request, code: str):
    """Switch language (sets a cookie), then bounce back where you came from."""
    resp = RedirectResponse(request.headers.get("referer") or "/", status_code=303)
    if code in i18n.LANGS:
        resp.set_cookie("lang", code, max_age=31536000, samesite="lax")
    return resp
