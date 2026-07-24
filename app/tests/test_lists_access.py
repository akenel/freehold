"""Access control on the list-intake routes — one test per hole that was open.

These are the findings an adversarial review pass confirmed after the feature was
already deployed to sandbox. Every one of them is "a logged-in user does something
to a file that isn't theirs", which for a product whose whole pitch is *your data,
your box* is the worst possible class of bug. Each fix gets a test so it stays shut.
"""
import enrich
import lists
from routers.lists import _owned

ALICE = {"username": "alice"}
BOB = {"username": "bob"}


def test_owned_is_the_single_source_of_truth_for_draft_access():
    alices = {"token": "a" * 32, "owner": "alice"}
    assert _owned(alices, ALICE) is True
    assert _owned(alices, BOB) is False


def test_a_missing_draft_is_not_an_access_failure():
    # The routes render "that draft is gone" for this, which leaks nothing.
    # Returning False here would 403 on a token that simply expired.
    assert _owned(None, BOB) is True
    assert _owned({}, BOB) is True


def test_an_ownerless_legacy_draft_stays_reachable():
    # Drafts written before ownership existed carry no owner; refusing them all
    # would strand work already in flight rather than protect anything.
    assert _owned({"token": "c" * 32}, BOB) is True


def test_open_drafts_filters_by_owner():
    # The index used to call open_drafts() with no argument, so the filter below
    # was written and never applied — and the row template renders each token as
    # a link, which handed every user everyone else's draft tokens.
    rows = [{"token": "a" * 32, "owner": "alice"}, {"token": "b" * 32, "owner": "bob"}]

    def fake(_prefix):
        return ["drafts/a.json", "drafts/b.json"]

    real_prefix, real_get = lists.vault.list_prefix, lists.vault.get_json
    try:
        lists.vault.list_prefix = fake
        lists.vault.get_json = lambda name: rows[0] if name.endswith("a.json") else rows[1]
        assert [d["owner"] for d in lists.open_drafts("alice")] == ["alice"]
        assert [d["owner"] for d in lists.open_drafts("bob")] == ["bob"]
        assert len(lists.open_drafts()) == 2      # bare call is the caller's bug, not ours
    finally:
        lists.vault.list_prefix, lists.vault.get_json = real_prefix, real_get


def test_source_ownership_is_recorded_beside_the_file_not_in_the_draft():
    # The source outlives its draft: the draft is discarded at approval, the
    # .xlsx stays so a recipe can be re-run. So ownership needs its own record,
    # or /lists/source/<key> degrades to "any user may download any workbook".
    key = "src/" + "d" * 32 + ".xlsx"
    assert lists.owner_key(key) == key + ".owner.json"

    store = {}
    real_put, real_get = lists.vault.put_json, lists.vault.get_json
    try:
        lists.vault.put_json = lambda obj, k: store.__setitem__(k, obj) or k
        lists.vault.get_json = lambda k: store.get(k)
        lists.vault.put_json({"owner": "alice"}, lists.owner_key(key))
        assert lists.source_owner(key) == "alice"
        assert lists.source_owner("src/" + "e" * 32 + ".xlsx") == ""   # unknown -> deny
    finally:
        lists.vault.put_json, lists.vault.get_json = real_put, real_get


def test_a_model_confidence_that_is_not_a_number_cannot_crash_a_run():
    # Raw float() on model output raised ValueError out of enrich(), through the
    # caller, into a 500 — after the recipe was saved and the draft deleted.
    assert enrich.as_confidence("high") == 0.0
    assert enrich.as_confidence(None) == 0.0
    assert enrich.as_confidence(float("nan")) == 0.0
    assert enrich.as_confidence(4.2) == 1.0
    assert enrich.as_confidence(-1) == 0.0
    assert enrich.as_confidence("0.85") == 0.85
    # ...and zero is the safe direction: the gate sends it to a human.
    assert enrich.gate(enrich.as_confidence("high")) == enrich.REJECTED
