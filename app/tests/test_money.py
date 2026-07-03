"""Money formatting is penny-exact and locale-correct — including India's lakh/crore."""
import money


def test_locale_formatting_exact():
    # one base CHF amount, written the way each market actually writes it
    assert money.format_money(123456.78, "CHF") == "CHF 123'456.78"
    assert money.format_money(123456.78, "EUR") == "128.395,05 €"
    assert money.format_money(123456.78, "USD") == "$138,271.59"
    assert money.format_money(123456.78, "INR") == "₹1,16,04,937.32"


def test_indian_grouping():
    assert money._group_indian("100") == "100"
    assert money._group_indian("1000") == "1,000"
    assert money._group_indian("100000") == "1,00,000"
    assert money._group_indian("11604937") == "1,16,04,937"


def test_convert_uses_rate():
    assert money.convert(1.0, "INR") == 94.0
    assert money.convert(10.0, "CHF") == 10.0
