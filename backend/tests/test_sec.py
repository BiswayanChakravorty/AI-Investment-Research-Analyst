from app.sec import latest_annual

def record(start, end, filed, value, form="10-K", fp="FY"):
    return {"start": start, "end": end, "filed": filed, "val": value, "form": form, "fp": fp, "accn": "sample"}

def test_latest_annual_ignores_quarters():
    facts = {"us-gaap": {"Revenues": {"units": {"USD": [
        record("2023-01-01", "2023-12-31", "2024-02-01", 100),
        record("2024-01-01", "2024-12-31", "2025-02-01", 120),
        record("2025-01-01", "2025-03-31", "2025-04-01", 999, "10-Q", "Q1"),
    ]}}}}
    assert latest_annual(facts, ["Revenues"])["value"] == 120

def test_latest_annual_rejects_missing():
    assert latest_annual({}, ["Revenues"]) is None

def test_latest_annual_prefers_amendment():
    facts = {"us-gaap": {"NetIncomeLoss": {"units": {"USD": [
        record("2024-01-01", "2024-12-31", "2025-02-01", 50),
        record("2024-01-01", "2024-12-31", "2025-03-01", 55, "10-K/A"),
    ]}}}}
    assert latest_annual(facts, ["NetIncomeLoss"])["value"] == 55
