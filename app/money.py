"""Freehold — multi-currency + locale-aware money formatting.

A taste of enterprise depth. One base amount, converted and written the way each
market actually writes numbers — including Indian lakh/crore grouping. The rates
here are illustrative constants; in production you pull a live feed (ECB reference
rates, an FX API) behind this exact same interface.
"""
BASE = "CHF"

CURRENCIES = {
    "CHF": {"symbol": "CHF", "pos": "pre",  "group": "swiss",    "rate": 1.00, "label": "Swiss franc"},
    "EUR": {"symbol": "€",   "pos": "post", "group": "european", "rate": 1.04, "label": "Euro"},
    "USD": {"symbol": "$",   "pos": "pre",  "group": "western",  "rate": 1.12, "label": "US dollar"},
    "INR": {"symbol": "₹",   "pos": "pre",  "group": "indian",   "rate": 94.0, "label": "Indian rupee"},
}

GROUP_LABEL = {
    "swiss": "apostrophe (1'234'567)",
    "european": "dot + comma (1.234.567,89)",
    "western": "comma (1,234,567)",
    "indian": "lakh / crore (12,34,567)",
}


def convert(amount_base: float, to: str) -> float:
    return amount_base * CURRENCIES[to]["rate"]


def _group_indian(digits: str) -> str:
    """India groups the last 3 digits, then in pairs: 11604937 -> 1,16,04,937."""
    if len(digits) <= 3:
        return digits
    last3, rest, parts = digits[-3:], digits[:-3], []
    while len(rest) > 2:
        parts.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest:
        parts.insert(0, rest)
    return ",".join(parts) + "," + last3


def _group(digits: str, style: str) -> str:
    if style == "indian":
        return _group_indian(digits)
    western = f"{int(digits):,}"          # 1,234,567
    if style == "swiss":
        return western.replace(",", "'")
    if style == "european":
        return western.replace(",", ".")
    return western


def format_money(amount_base: float, ccy: str) -> str:
    cfg = CURRENCIES[ccy]
    value = abs(convert(amount_base, ccy))
    whole = int(value)
    cents = int(round((value - whole) * 100))
    if cents == 100:
        whole, cents = whole + 1, 0
    grouped = _group(str(whole), cfg["group"])
    dec = "," if cfg["group"] == "european" else "."
    number = f"{grouped}{dec}{cents:02d}"
    if cfg["pos"] == "pre":
        return f"{cfg['symbol']}{' ' if ccy == 'CHF' else ''}{number}"
    return f"{number} {cfg['symbol']}"
