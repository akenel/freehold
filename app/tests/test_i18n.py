"""i18n resolves the right language, falls back to English, and interpolates."""
import types

import i18n


def test_hindi_catalog_loads():
    t = i18n.translator("hi")
    assert t("index.standing") == "फ्रीहोल्ड खड़ा है।"


def test_missing_key_falls_back_to_the_key():
    t = i18n.translator("hi")
    assert t("nope.not.a.real.key") == "nope.not.a.real.key"


def test_unknown_language_falls_back_to_english():
    t = i18n.translator("xx")
    assert t("index.standing") == "Freehold is standing."


def test_interpolation_respects_word_order():
    t = i18n.translator("hi")
    assert t("nav.signed_in", name="Sam") == "Sam के रूप में साइन इन"


def _req(query=None, cookies=None):
    return types.SimpleNamespace(query_params=query or {}, cookies=cookies or {})


def test_resolve_lang_prefers_query_then_cookie_then_english():
    assert i18n.resolve_lang(_req(query={"lang": "hi"})) == "hi"
    assert i18n.resolve_lang(_req(cookies={"lang": "hi"})) == "hi"
    assert i18n.resolve_lang(_req()) == "en"
    assert i18n.resolve_lang(_req(query={"lang": "zz"})) == "en"
