"""Five sample lists with KNOWN right answers — the golden corpus.

Each one is built to provoke exactly one behaviour, so when a run comes back
wrong you know which brake failed rather than staring at 45 rows of real data
wondering. `EXPECT` beside each grid is the contract: `test_samples.py` asserts
it, and `ops/make-test-sheets.py` writes the same five files to disk so the same
contract can be checked by hand in a browser on sandbox.

Deliberately small and boring. A fixture you cannot verify by eye is a fixture
that will one day be wrong and agree with the code about it.
"""

# --- 1. A clean list. The control. -----------------------------------------
# The point of this one is NEGATIVE: a tool that always finds ten things to fix
# is a tool nobody trusts on their good data. Nothing here needs repair.
CLEAN = [
    ["Company", "Contact", "Email", "Phone", "City"],
    ["Alpina AG", "R. Meier", "r.meier@alpina.ch", "+41445551234", "Zurich"],
    ["Bernina GmbH", "S. Frei", "s.frei@bernina.ch", "+41315559876", "Bern"],
    ["Cervin SA", "L. Dubois", "l.dubois@cervin.ch", "+41225554321", "Geneva"],
    ["Dolder AG", "T. Huber", "t.huber@dolder.ch", "+41445558765", "Zurich"],
]
CLEAN_EXPECT = {
    "rows": 4, "columns": 5,
    "quality_all_perfect": True,          # nothing missing anywhere
    "phone_resolved": 4,                  # every phone already E.164
    "phone_declined": 0,
    "no_reconcile_offered": True,         # only one phone column, nothing to compare
    "no_dedupe_offered": True,            # every value distinct
}

# --- 2. Messy phones. The rules' exam paper. -------------------------------
# Two columns claiming the same fact, in every disagreement shape there is.
# Every expected value below was worked out by hand, not read off a run.
MESSY_PHONES = [
    ["Agency", "Phone", "Contact details"],
    # agree — the (0) trunk prefix must not read as a conflict
    ["Eursap NL", "+31 20 890 8064", "Amsterdam +31 (0) 20 890 8064"],
    # only the left column has a number at all
    ["Hays CH", "+41 44 225 50 00", "info@hays.ch, no phone listed"],
    # conflict — two genuinely different offices
    ["Westhouse", "+49 89 3837720", "Zurich office +41 43 931 57 00"],
    # extension glued on: prefix of the other, still a human decision
    ["Montash", "+44 20 7014 0233", "+44 20 7014 0233 100"],
    # rules must DECLINE: two numbers in one cell, no way to pick
    ["Michael Bailey", "+31 207 975 000 or +44 207 549 4040", "Amsterdam"],
    # rules must DECLINE: 10 digits but leading 0 — not NANP, unknown country
    ["Local NL", "020 36 30 310", "Amsterdam"],
    # not a phone number in any sense
    ["Freelancermap", "freelancermap.com/freelancer", "web only"],
]
MESSY_EXPECT = {
    "rows": 7,
    # (row label -> what enrich.candidates must return for the Phone column)
    "candidates": {
        "Eursap NL": ["+31208908064"],
        "Hays CH": ["+41442255000"],
        "Westhouse": ["+49893837720"],
        "Montash": ["+442070140233"],
        "Michael Bailey": ["+31207975000", "+442075494040"],   # two -> decline
        "Local NL": [],                                        # leading 0 -> decline
        "Freelancermap": [],
    },
    # phone_e164 resolves only when there is EXACTLY one candidate
    "resolved_by_rule": ["Eursap NL", "Hays CH", "Westhouse", "Montash"],
    "declined_by_rule": ["Michael Bailey", "Local NL", "Freelancermap"],
    "reconcile": {
        "Eursap NL": "agree",
        "Hays CH": "only_phone",
        "Westhouse": "conflict",
        "Montash": "conflict",          # prefix-plus-extension is still not equal
        # Two of these I got WRONG when writing them by hand, and the corpus
        # caught me rather than the other way round — which is the argument for
        # writing expectations before running anything:
        #   Michael Bailey: the left cell holds two numbers, the right cell is
        #     just "Amsterdam". Nothing to overlap WITH, so it is only_phone.
        #   Local NL: "020 36 30 310" is declined (leading 0, unknown country)
        #     and "Amsterdam" has none either — zero candidates on both sides
        #     means there is no disagreement to report at all, hence None.
        "Michael Bailey": "only_phone",
        "Local NL": None,
        "Freelancermap": None,          # no numbers on either side
    },
}

# --- 3. Notes living in the data. The row that isn't a record. -------------
# Every real spreadsheet grows a tail: totals, section headers, a reminder to
# self. They occupy the same columns and no database would ever have allowed it.
NOTES_IN_DATA = [
    ["Agency", "Market", "Phone", "Next step"],
    ["Alpina AG", "CH", "+41445551234", "Call Tuesday"],
    ["Bernina GmbH", "CH / DE", "+41315559876", "Email sent"],
    ["Cervin SA", "CH / FR", "+41225554321", "Waiting"],
    [],                                     # the blank spacer row
    ["PROGRESS"],                           # a heading in column A
    ["Calls made"],
    ["3 of 12 done"],
    ["BEST TIME TO CALL"],
    ["Tuesday to Thursday, 09:30-11:00"],
]
NOTES_EXPECT = {
    # the blank row is dropped by the reader; the note rows are NOT — they look
    # like records to a reader and must be caught later, by the quality score.
    "rows": 8,
    "real_records": 3,
    "note_rows": 5,
    # a note row has one cell of four filled
    "quality_of_notes": 0.25,
    "quality_of_records": 1.0,
}

# --- 4. Dirty headers. The reader's exam paper. ----------------------------
DIRTY_HEADERS = [
    ["PHONE", "phone", "", "Full Name!", "Ort / City", "PHONE"],
    ["+41445551234", "044 555 12 34", "x", "R. Meier", "Zurich", "+41445551234"],
    ["+41315559876", "031 555 98 76", "y", "S. Frei", "Bern", "+41315559876"],
]
DIRTY_EXPECT = {
    # duplicates get _2/_3, the blank header becomes "col", punctuation is
    # stripped, and a slash-separated header collapses to one underscore.
    "fields": ["phone", "phone_2", "col", "full_name", "ort_city", "phone_3"],
    "rows": 2,
}

# --- 5. Several tabs. The one-list-per-upload rule. ------------------------
# Freehold reads ONE tab. This proves the picker sees all of them and that
# choosing tab N actually reads tab N — the bug that silently imports the
# wrong sheet is the worst kind, because the output looks perfectly fine.
TAB_A = [["Agency", "Phone"], ["Alpina AG", "+41445551234"]]
TAB_B = [["Product", "Price", "Category"], ["Bubble Gum 8g", "12.50", "edible"]]
TAB_C = [["Invoice", "Amount", "Due"], ["INV-001", "480.00", "2026-08-31"]]
MULTI_TABS = [TAB_A, TAB_B, TAB_C]
MULTI_NAMES = ("Call List", "Catalogue", "Invoices")
MULTI_EXPECT = {
    "sheet_names": ["Call List", "Catalogue", "Invoices"],
    "fields_by_tab": {0: ["agency", "phone"],
                      1: ["product", "price", "category"],
                      2: ["invoice", "amount", "due"]},
}

SAMPLES = {
    "1-clean-contacts": (CLEAN, ("Contacts",)),
    "2-messy-phones": (MESSY_PHONES, ("Agencies",)),
    "3-notes-in-the-data": (NOTES_IN_DATA, ("Call List",)),
    "4-dirty-headers": (DIRTY_HEADERS, ("Sheet1",)),
    "5-several-tabs": (MULTI_TABS, MULTI_NAMES),
}
