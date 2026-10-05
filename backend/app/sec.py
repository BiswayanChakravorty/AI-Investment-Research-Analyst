"""SEC EDGAR company identity and annual XBRL financial facts.

The SEC Company Facts endpoint is the source of truth for normalized US-GAAP
facts in this first production-oriented ingestion layer.
"""
import os
from datetime import date
import httpx

HEADERS = {
    "User-Agent": os.getenv(
        "SEC_USER_AGENT",
        "AIInvestmentResearchAnalyst research@example.com",
    ),
    "Accept-Encoding": "gzip, deflate",
}

TAGS = {
    "revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
    ],
    "net_income": ["NetIncomeLoss"],
    "operating_income": ["OperatingIncomeLoss"],
    "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
    "capital_expenditure": ["PaymentsToAcquirePropertyPlantAndEquipment"],
    "eps": ["EarningsPerShareDiluted"],
}


def _annual_records(facts: dict, tags: list[str], unit: str = "USD") -> list[dict]:
    candidates = []
    for tag in tags:
        records = facts.get("us-gaap", {}).get(tag, {}).get("units", {}).get(unit, [])
        for record in records:
            if record.get("form") not in ("10-K", "10-K/A") or record.get("fp") != "FY":
                continue
            if not all(k in record for k in ("start", "end", "filed", "val")):
                continue
            try:
                duration = (date.fromisoformat(record["end"]) - date.fromisoformat(record["start"])).days
            except ValueError:
                continue
            if not 330 <= duration <= 380:
                continue
            candidates.append(record | {"tag": tag})
    # Deduplicate equivalent filings/periods while retaining the latest filing.
    candidates.sort(key=lambda r: (r["end"], r["filed"]), reverse=True)
    return candidates


def annual_facts(facts: dict, tags: list[str], unit: str = "USD") -> list[dict]:
    records = _annual_records(facts, tags, unit)
    periods = {}
    for record in records:
        key = record["end"]
        if key not in periods:
            periods[key] = {
                "value": record["val"],
                "end": record["end"],
                "start": record.get("start"),
                "filed": record["filed"],
                "tag": record["tag"],
                "accession": record.get("accn"),
            }
    return sorted(periods.values(), key=lambda r: r["end"], reverse=True)


def latest_annual(facts, tags, unit="USD"):
    records = annual_facts(facts, tags, unit)
    return records[0] if records else None


async def fetch_sec_financials(ticker: str):
    async with httpx.AsyncClient(timeout=25, headers=HEADERS) as client:
        index = await client.get("https://www.sec.gov/files/company_tickers.json")
        index.raise_for_status()
        matches = [v for v in index.json().values() if v["ticker"].upper() == ticker.upper()]
        if not matches:
            return None

        match = matches[0]
        cik = str(match["cik_str"]).zfill(10)
        response = await client.get(
            f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        )
        response.raise_for_status()
        data = response.json()

    facts = data.get("facts", {})
    metrics = {
        name: latest_annual(facts, tags, "USD/shares" if name == "eps" else "USD")
        for name, tags in TAGS.items()
    }
    history = {
        name: annual_facts(facts, tags, "USD/shares" if name == "eps" else "USD")[:5]
        for name, tags in TAGS.items()
    }

    revenue = metrics["revenue"]
    income = metrics["operating_income"]
    cash = metrics["operating_cash_flow"]
    capex = metrics["capital_expenditure"]

    operating_margin = (
        100 * income["value"] / revenue["value"]
        if revenue and income and revenue["end"] == income["end"] and revenue["value"]
        else None
    )
    free_cash_flow = (
        cash["value"] - capex["value"]
        if cash and capex and cash["end"] == capex["end"]
        else None
    )

    revenue_growth = None
    revenue_history = history["revenue"]
    if len(revenue_history) >= 2:
        current, prior = revenue_history[0], revenue_history[1]
        if current["value"] is not None and prior["value"]:
            revenue_growth = 100 * (current["value"] / prior["value"] - 1)

    return {
        "cik": cik,
        "name": data.get("entityName") or match["title"],
        "metrics": metrics,
        "history": history,
        "revenue_growth_pct": revenue_growth,
        "operating_margin_pct": operating_margin,
        "free_cash_flow": free_cash_flow,
        "url": f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
    }
