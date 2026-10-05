"""SEC EDGAR company identity and annual XBRL financial facts."""
import os
import httpx

HEADERS = {"User-Agent": os.getenv("SEC_USER_AGENT", "AIInvestmentResearchAnalyst research contact research@example.com"), "Accept-Encoding": "gzip, deflate"}

TAGS = {
    "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet", "RevenueFromContractWithCustomerIncludingAssessedTax"],
    "net_income": ["NetIncomeLoss"],
    "operating_income": ["OperatingIncomeLoss"],
    "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
    "capital_expenditure": ["PaymentsToAcquirePropertyPlantAndEquipment"],
    "eps": ["EarningsPerShareDiluted"],
}

def latest_annual(facts, tags, unit="USD"):
    """Use annual FY forms and select latest filed comparable record."""
    candidates = []
    for tag in tags:
        records = facts.get("us-gaap", {}).get(tag, {}).get("units", {}).get(unit, [])
        for record in records:
            if record.get("form") not in ("10-K", "10-K/A") or record.get("fp") != "FY":
                continue
            if not all(k in record for k in ("start", "end", "filed", "val")):
                continue
            from datetime import date
            try:
                duration = (date.fromisoformat(record["end"]) - date.fromisoformat(record["start"])).days
            except ValueError:
                continue
            if not 330 <= duration <= 380:
                continue
            candidates.append((record["end"], record["filed"], tag, record))
    if not candidates:
        return None
    end, filed, tag, record = max(candidates, key=lambda x: (x[0], x[1]))
    return {"value": record["val"], "end": end, "filed": filed, "tag": tag, "accession": record.get("accn")}

async def fetch_sec_financials(ticker):
    async with httpx.AsyncClient(timeout=25, headers=HEADERS) as client:
        index = await client.get("https://www.sec.gov/files/company_tickers.json")
        index.raise_for_status()
        matches = [v for v in index.json().values() if v["ticker"].upper() == ticker.upper()]
        if not matches:
            return None
        match = matches[0]
        cik = str(match["cik_str"]).zfill(10)
        response = await client.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json")
        response.raise_for_status()
        data = response.json()
    facts = data.get("facts", {})
    metrics = {name: latest_annual(facts, tags, "USD/shares" if name == "eps" else "USD") for name, tags in TAGS.items()}
    revenue = metrics["revenue"]
    income = metrics["operating_income"]
    cash = metrics["operating_cash_flow"]
    capex = metrics["capital_expenditure"]
    # Never combine mismatched reporting periods in derived financial metrics.
    operating_margin = (100 * income["value"] / revenue["value"]
                        if revenue and income and revenue["end"] == income["end"] and revenue["value"] else None)
    fcf = (cash["value"] - capex["value"]
           if cash and capex and cash["end"] == capex["end"] else None)
    return {"cik": cik, "name": data.get("entityName") or match["title"], "metrics": metrics,
            "operating_margin_pct": operating_margin, "free_cash_flow": fcf,
            "url": f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"}
