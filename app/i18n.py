"""Freehold — tiny, transparent i18n.

Translation catalogs are plain JSON files in locales/ (one per language). A
context processor injects `t`, `lang`, and `langs` into every template, so any
page can say {{ t('some.key') }} with no per-route wiring. Language is chosen by
?lang= (which sets a cookie) or the cookie, falling back to English.

To add a language: drop locales/<code>.json and add it to LANGS. That's it.
"""
import json
from pathlib import Path

LOCALES = Path(__file__).parent / "locales"
LANGS = {"en": "English", "hi": "हिन्दी"}

_catalog: dict[str, dict] = {}
for _code in LANGS:
    _f = LOCALES / f"{_code}.json"
    _catalog[_code] = json.loads(_f.read_text(encoding="utf-8")) if _f.exists() else {}


def translator(lang: str):
    lang = lang if lang in LANGS else "en"

    def t(key: str, **kw) -> str:
        text = _catalog.get(lang, {}).get(key) or _catalog["en"].get(key) or key
        return text.format(**kw) if kw else text

    return t


def resolve_lang(request) -> str:
    q = request.query_params.get("lang")
    if q in LANGS:
        return q
    cookie = request.cookies.get("lang")
    return cookie if cookie in LANGS else "en"
