"""The door: OIDC login/register/callback/logout, and the first rooms behind it
(dashboard · console · account)."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

import audit
import auth
import deps
import i18n
import media
import profiles
from deps import APP_BASE_URL, APP_ENV, KC_PUBLIC_URL, KC_REALM, admin_or_deny, templates

router = APIRouter()


@router.get("/login")
async def login(request: Request):
    state, nonce = auth.new_secret(), auth.new_secret()
    verifier, challenge = auth.make_pkce()
    request.session["oauth"] = {"state": state, "nonce": nonce, "cv": verifier}
    redirect_uri = f"{APP_BASE_URL}/auth/callback"
    lang = i18n.resolve_lang(request)  # carry the app language into the login page
    return RedirectResponse(
        auth.build_auth_redirect(redirect_uri, state, nonce, challenge, ui_locales=lang)
    )


@router.get("/register")
async def register(request: Request):
    """Self-serve sign-up — Keycloak's registration page. New users land back at
    /auth/callback already logged in (same code path as login)."""
    state, nonce = auth.new_secret(), auth.new_secret()
    verifier, challenge = auth.make_pkce()
    request.session["oauth"] = {"state": state, "nonce": nonce, "cv": verifier}
    redirect_uri = f"{APP_BASE_URL}/auth/callback"
    lang = i18n.resolve_lang(request)
    return RedirectResponse(
        auth.build_register_redirect(redirect_uri, state, nonce, challenge, ui_locales=lang)
    )


@router.get("/auth/callback")
async def auth_callback(request: Request):
    saved = request.session.get("oauth") or {}
    code = request.query_params.get("code")
    if not code or request.query_params.get("state") != saved.get("state"):
        # Almost always a Back-button replay of an already-consumed callback (a
        # successful login pops the one-time state below), or a stale tab. The
        # spent state is the anti-forgery check doing its job — no session is
        # minted here. So don't show a scary error: if they're already in, send
        # them home; otherwise start a clean login.
        if deps.current_user(request):
            return RedirectResponse("/dashboard", status_code=303)
        return RedirectResponse("/login", status_code=303)
    redirect_uri = f"{APP_BASE_URL}/auth/callback"
    try:
        tokens = await auth.exchange_code(code, redirect_uri, saved["cv"])
        claims = auth.verify_id_token(tokens["id_token"], saved.get("nonce"))
        roles = auth.roles_from_access(tokens["access_token"])
    except Exception as exc:  # noqa: BLE001
        return HTMLResponse(f"Login failed: {exc}", status_code=400)

    request.session.pop("oauth", None)
    request.session["user"] = {
        "username": claims.get("preferred_username"),
        "name": claims.get("name") or claims.get("preferred_username"),
        "email": claims.get("email"),
        "roles": roles,
    }
    prof = await profiles.get(request.session["user"]["username"])
    request.session["user"]["avatar"] = media.url(prof.avatar_key) if prof else ""
    request.session["id_token"] = tokens["id_token"]
    await audit.record(request.session["user"]["username"], audit.LOGIN, roles=roles)
    return RedirectResponse("/dashboard", status_code=303)


@router.get("/logout")
async def logout(request: Request):
    id_token = request.session.get("id_token")
    user = deps.current_user(request)
    if user:
        await audit.record(user.get("username"), audit.LOGOUT)
    request.session.clear()
    if id_token:
        return RedirectResponse(auth.logout_redirect(id_token, f"{APP_BASE_URL}/"))
    return RedirectResponse("/")


@router.get("/dashboard")
async def dashboard(request: Request):
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("dashboard.html", {
        "request": request, "user": user, "env": APP_ENV, "realm": KC_REALM,
    })


@router.get("/console")
async def console(request: Request):
    """RBAC demo: admins only. A logged-in 'staff' user gets a clean 403."""
    user, denied = admin_or_deny(request)
    if denied:
        return denied
    return templates.TemplateResponse("console.html", {"request": request, "user": user})


@router.get("/account")
async def account(request: Request):
    user = deps.current_user(request)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("account.html", {
        "request": request, "user": user, "env": APP_ENV, "realm": KC_REALM, "kc_url": KC_PUBLIC_URL,
    })
