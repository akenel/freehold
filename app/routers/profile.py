"""Profiles — the public town-square page, Markdown bios, avatar/banner uploads."""
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

import deps
import media
import profiles
from deps import templates

router = APIRouter()

SAMPLE_BIO = """## About me

Hey — I'm **{name}**, and this is my corner of the town square.

- 🛠️ I like to build things
- 🌍 I believe in *owning my stack*
- 🐺 Say hi anytime

> This bio is **Markdown** — headers, **bold**, lists and quotes all render.
> Hit **Edit profile** and make it your own."""


async def _seed_if_missing(user: dict):
    """Everyone starts with a filled-in profile — no blank page."""
    profile = await profiles.get(user["username"])
    if profile is None:
        name = user.get("name") or user["username"]
        profile = await profiles.upsert(
            user["username"], display_name=name, tagline="New in the piazza",
            bio=SAMPLE_BIO.format(name=name),
            links=[{"label": "YouTube", "url": "https://youtube.com"},
                   {"label": "LinkedIn", "url": "https://linkedin.com"}],
        )
    return profile


def _profile_ctx(request: Request, profile, viewer, is_owner: bool) -> dict:
    return {
        "request": request, "user": viewer, "profile": profile, "is_owner": is_owner,
        "avatar_url": media.url(profile.avatar_key), "banner_url": media.url(profile.banner_key),
    }


@router.get("/profile")
async def my_profile(request: Request):
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    profile = await _seed_if_missing(user)
    return templates.TemplateResponse("profile.html", _profile_ctx(request, profile, user, True))


@router.get("/u/{username}")
async def public_profile(request: Request, username: str):
    profile = await profiles.get(username)
    if profile is None:
        return templates.TemplateResponse(
            "404.html", {"request": request, "user": deps.current_user(request)}, status_code=404)
    viewer = deps.current_user(request)
    is_owner = bool(viewer and viewer.get("username") == username)
    return templates.TemplateResponse("profile.html", _profile_ctx(request, profile, viewer, is_owner))


@router.get("/profile/edit")
async def edit_profile(request: Request):
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    profile = await _seed_if_missing(user)
    return templates.TemplateResponse("profile_edit.html", _profile_ctx(request, profile, user, True))


@router.post("/profile/edit")
async def save_profile(request: Request):
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    form = await request.form()
    fields = {
        "display_name": (form.get("display_name") or "").strip()[:120],
        "tagline": (form.get("tagline") or "").strip()[:160],
        "bio": (form.get("bio") or "").strip(),
    }
    # links come as parallel label[]/url[] rows; keep the ones with a URL
    pairs = zip(form.getlist("link_label"), form.getlist("link_url"))
    fields["links"] = [{"label": (l or "").strip()[:60], "url": u.strip()[:300]}
                       for l, u in pairs if u and u.strip()]
    # uploads: avatar + banner -> MinIO (only if a real image was sent)
    for field, attr in (("avatar", "avatar_key"), ("banner", "banner_key")):
        upload = form.get(field)
        if upload is not None and getattr(upload, "filename", ""):
            data = await upload.read()
            if data and media.is_image(upload.content_type) and len(data) <= 5 * 1024 * 1024:
                fields[attr] = media.save_image(data, upload.content_type)
    profile = await profiles.upsert(user["username"], **fields)
    request.session["user"]["avatar"] = media.url(profile.avatar_key)  # refresh topbar
    return RedirectResponse("/profile", status_code=303)
