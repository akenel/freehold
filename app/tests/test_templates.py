"""Render the three list templates for real, with realistic context.

A template that "looks right" in a diff is not verified. These render through
Jinja with the same loader the app uses (the two shared includes stubbed, since
_topbar/_footer need the request object and the context processor), against
context built by actually running xray + analyze + recipes — not by hand-writing
the dicts the template happens to want. If the route and the template ever
disagree about a key, this is where it shows up.
"""
import asyncio
import os
import types

# db.py builds an engine at import time; business_hub imports it. A DSN that
# parses is enough — nothing here ever opens a connection.
os.environ.setdefault("DATABASE_URL", "postgresql://freehold:x@localhost:5432/freehold")
from datetime import datetime, timezone

import pytest
from markupsafe import escape
from jinja2 import ChoiceLoader, DictLoader, Environment, FileSystemLoader, StrictUndefined

import actions
import analyze
import enrich
import recipes
import xray
from tests._xlsx import make_xlsx

import inbound

STUBS = {"_topbar.html": "<!--topbar-->", "_footer.html": "<!--footer-->"}
ENV = Environment(
    loader=ChoiceLoader([DictLoader(STUBS), FileSystemLoader("templates")]),
    undefined=StrictUndefined, autoescape=True,
)

GRID = [["Agentur", "Telefon", "Telefon", "Status", "Erfasst", "Markt", "E-Mail"]] + [
    ["Havas Media", "+41 44 668 18 00", "+41 44 668 18 00", "Active", 45231, "CH / DE",
     "info@havas.ch"],
    ["havas media", "+41 44 668 18 00", "+41 79 111 22 33", "active", 45232, "FR / DE",
     "info@havas.ch"],
    ["Dentsu CH", "+41 43 210 10 10", "", "ACTIVE", 45233, "CH", "a@dentsu.ch"],
    ["Serviceplan Suisse", "+41 61 500 10 10", "", "Closed", 45234, "CH / AT",
     "kontakt@serviceplan.ch"],
]


@pytest.fixture(scope="module")
def draft():
    blob = make_xlsx(GRID, sheet_names=("Kontakte", "Notizen"))
    fields, records = inbound.read_xlsx(blob)
    xr = xray.xray(fields, records, "Agenturen 2024.xlsx", "Kontakte")
    analysis, stats = asyncio.run(analyze.analyze(xr, model="none", records=records))
    return {
        "token": "a" * 32, "src_key": "src/" + "b" * 32 + ".xlsx",
        "filename": "Agenturen 2024.xlsx", "owner": "angel",
        "at": "2026-07-24T09:14:00+00:00", "sheet": 0,
        "tabs": [{"index": 0, "name": "Kontakte", "headers": fields[:8]},
                 {"index": 1, "name": "Notizen", "headers": ["col"]}],
        "xray": xr, "analysis": analysis, "stats": stats,
    }


def _run_row(source):
    return types.SimpleNamespace(
        run_at=datetime(2026, 7, 24, 9, 12, tzinfo=timezone.utc), source=source,
        count=4, model="gpt-oss:120b", enriched_count=4, tokens=3140, review_count=1,
        report_key="c" * 32 + ".json", run_by="angel")


def test_lists_index_renders():
    html = ENV.get_template("lists.html").render(
        request=None, user={"username": "angel", "roles": ["admin"]}, error="",
        models=enrich.MODELS, default_model=enrich.DEFAULT_MODEL,
        recipes=[{"key": "agenturen-2024", "label": "Media agency call list", "current": 3,
                  "archived": False, "approved_by": "angel",
                  "approved_at": "2026-06-30T10:00:00+00:00", "spec_sha": "4f9c1a" * 6,
                  "versions": 3, "actions": ["normalize_phone", "dedupe"]}],
        drafts=[{"token": "a" * 32, "filename": "Agenturen 2024.xlsx",
                 "at": "2026-07-24T09:14:00+00:00", "rows": 480,
                 "model": "gpt-oss:120b", "owner": "angel"}],
        runs=[_run_row("Agenturen 2024.xlsx → agenturen-2024 v3")],
        row_limit=5000, max_mb=10, lang="en")
    for needle in ("Every list is a table that never got a schema",
                   "/lists/upload", "enctype=\"multipart/form-data\"",
                   "Media agency call list", "/lists/recipe/agenturen-2024",
                   "/lists/draft/" + "a" * 32,
                   # The disclosure must match what analyze.py actually sends.
                   # This used to pin the phrase "Never the sheet", which was
                   # false — profile_payload() ships the first three rows whole,
                   # real cell values and all. A test that pins a wrong promise
                   # is worse than no test: it defends the lie.
                   "the first three rows in full",
                   "nothing leaves at all",
                   "🐺 Honest caveat", "<!--topbar-->", "<!--footer-->"):
        assert needle in html, needle
    assert "Never the sheet" not in html


def test_lists_index_renders_its_empty_states():
    html = ENV.get_template("lists.html").render(
        request=None, user={"username": "angel"}, error="Pick a file first.",
        models=enrich.MODELS, default_model=enrich.DEFAULT_MODEL,
        recipes=[], drafts=[], runs=[], row_limit=5000, max_mb=10, lang="en")
    assert "Pick a file first." in html
    assert "That's how a recipe is born" in html
    assert "No list runs yet" in html


def test_the_draft_screen_renders_every_number_and_every_action(draft):
    xr, analysis = draft["xray"], draft["analysis"]
    acts = analysis["actions"]
    html = ENV.get_template("list_draft.html").render(
        request=None, user={"username": "angel"}, error="", draft=draft,
        xr=xr, analysis=analysis, stats=draft["stats"],
        auto=[a for a in acts if a["gate"] == enrich.AUTO],
        review=[a for a in acts if a["gate"] == enrich.REVIEW],
        rejected=[a for a in acts if a["gate"] == enrich.REJECTED],
        classify=next((a for a in acts if a["id"] == "classify"), None),
        columns=xr["columns"], models=enrich.MODELS, default_model="gpt-oss:120b",
        auto_above=enrich.AUTO_ABOVE, review_above=enrich.REVIEW_ABOVE,
        slow=False, calls=1, lang="en")

    # the deterministic story
    assert str(escape(analysis["summary"]["value"])) in html
    assert f"<b>{xr['row_count']}</b>" in html
    for f in xr["findings"]:
        assert str(escape(f["text"])) in html, f["code"]
    assert "counted</b>, not guessed" in html

    # every licensed action is on the page as a tickable checkbox
    for a in acts:
        value = f'{a["id"]}:{"|".join(a["columns"])}'
        assert f'name="action" value="{value}"' in html, value
    assert 'name="confirm"' in html and "Approve &amp; run" in html
    assert f'/lists/draft/{draft["token"]}/approve' in html
    assert f'/lists/draft/{draft["token"]}/discard' in html
    assert f'/lists/source/{draft["src_key"]}' in html
    # the two provenance tags, one meaning each
    assert 'class="tag by-rule"' in html and "🐺 Honest caveat" in html


def test_the_draft_screen_shows_the_classify_editor_when_one_is_offered(draft):
    acts = draft["analysis"]["actions"]
    cls = [a for a in acts if a["id"] == "classify"]
    assert cls, "the fixture sheet should licence a classify"
    html = ENV.get_template("list_draft.html").render(
        request=None, user={"username": "angel"}, error="", draft=draft,
        xr=draft["xray"], analysis=draft["analysis"], stats=draft["stats"],
        auto=[], review=cls, rejected=[], classify=cls[0],
        columns=draft["xray"]["columns"], models=enrich.MODELS,
        default_model="none", auto_above=0.9, review_above=0.7,
        slow=True, calls=20, lang="en")
    assert 'name="classify_taxonomy"' in html and 'name="classify_to"' in html
    assert 'name="classify_feed"' in html and 'name="classify_instruction"' in html
    for value in cls[0]["params"]["taxonomy"]:
        assert str(escape(value)) in html
    assert "sequential model calls" in html          # the honest slow warning


def test_the_recipe_screen_renders_the_chain_the_mapping_and_the_runs(draft):
    spec = recipes.build(draft["xray"], draft["analysis"], {
        "key": "agenturen-2024", "label": "Media agency call list", "note": "first pass",
        "actions": [f'{a["id"]}:{"|".join(a["columns"])}' for a in draft["analysis"]["actions"]],
        "quality_cols": [], "label_fields": ["agentur"],
        "classify_to": "markets", "classify_multi": True,
        "classify_taxonomy": ["CH", "DE", "AT", "Other"],
        "classify_instruction": "Normalize to ISO codes.", "classify_feed": [],
        "schema_table": "agenturen_2024", "parse_from": "excel_serial",
    })
    spec, warnings = recipes.validate(spec, list(draft["xray"]["columns"]))
    spec["version"] = 3
    sha = recipes.spec_sha(spec)
    version = {"version": 3, "spec": spec, "spec_sha": sha,
               "approved_by": "angel", "approved_at": "2026-06-30T10:00:00+00:00",
               "note": "first pass"}
    doc = {"key": "agenturen-2024", "label": "Media agency call list",
           "created_by": "angel", "created_at": "2026-04-11T10:00:00+00:00",
           "current": 3, "archived": False, "versions": [version]}

    html = ENV.get_template("list_recipe.html").render(
        request=None, user={"username": "angel"}, doc=doc, spec=spec,
        shown=version, chain=[version],
        runs=[_run_row("Agenturen 2024.xlsx → agenturen-2024 v3")],
        models=enrich.MODELS, default_model=enrich.DEFAULT_MODEL,
        last_src="src/" + "b" * 32 + ".xlsx", actions_meta=actions.ACTIONS, lang="en")

    assert "Media agency call list" in html and sha[:12] in html
    assert "/lists/recipe/agenturen-2024/run" in html
    for a in spec["actions"]:
        assert a["id"] in html
    assert "✨ model" in html or not any(
        actions.ACTIONS[a["id"]]["needs_model"] for a in spec["actions"])
    assert "⚙ rule" in html
    assert "/business-hub/report/" + "c" * 32 + ".json" in html
    assert "this compares <b>runs</b>, not answers" in html
    # validate() collapsed the duplicate singleton actions, and said so out loud.
    assert all("can only run once" in w for w in warnings), warnings
    shown_with = dict(version, warnings=warnings)
    loud = ENV.get_template("list_recipe.html").render(
        request=None, user={"username": "angel"}, doc=doc, spec=spec,
        shown=shown_with, chain=[shown_with], runs=[], models=enrich.MODELS,
        default_model=enrich.DEFAULT_MODEL, last_src="", actions_meta=actions.ACTIONS,
        lang="en")
    assert "What you ticked and what got saved are not identical" in loud
    for w in warnings:
        assert str(escape(w)) in loud


def test_the_business_hub_page_still_renders_with_the_new_report_url():
    import business_hub
    html = ENV.get_template("business_hub.html").render(
        request=None, user={"username": "angel"}, runs=[_run_row("demo")],
        source="jsonplaceholder (demo CRM)", report_url=business_hub.report_url,
        models=enrich.MODELS, default_model=enrich.DEFAULT_MODEL, latest={},
        auto_above=0.9, review_above=0.7, lang="en")
    assert "/business-hub/report/" + "c" * 32 + ".json" in html
    assert "/media/business-hub/" not in html          # the public link is gone
    assert "📋 Bring your own list →" in html
