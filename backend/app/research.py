from datetime import datetime, timezone
from .providers import AlphaVantageProvider
from .sec import fetch_sec_financials
from .models import ResearchReport, FinancialSnapshot, FinancialPeriod, Scenario, Evidence, ToneAnalysis
from .valuation import scenario_value

async def build_research_report(ticker):
    ticker = ticker.strip().upper()
    if not ticker.isalpha():
        raise ValueError("Ticker must contain alphabetic characters only.")

    evidence = []
    limitations = []
    sec = None
    try:
        sec = await fetch_sec_financials(ticker)
    except Exception as exc:
        limitations.append(f"SEC ingestion unavailable: {type(exc).__name__}.")

    if sec:
        metrics = sec["metrics"]

        def metric(name):
            item = metrics.get(name)
            if item:
                evidence.append(Evidence(
                    id=f"sec-{name}",
                    source_kind="sec",
                    title=f"SEC XBRL: {name}",
                    as_of=item["end"],
                    url=sec["url"],
                    fact_or_inference="fact",
                    summary=f"US-GAAP {item['tag']}; FY ended {item['end']}; filed {item['filed']}; accession {item['accession']}.",
                ))
                return item["value"]
            evidence.append(Evidence(
                id=f"sec-{name}",
                source_kind="sec",
                title=f"SEC XBRL: {name}",
                url=sec["url"],
                fact_or_inference="missing",
                summary="No qualifying annual US-GAAP value found.",
            ))
            return None

        revenue = metric("revenue")
        net_income = metric("net_income")
        eps = metric("eps")
        operating_income = metric("operating_income")
        operating_cash_flow = metric("operating_cash_flow")
        capital_expenditure = metric("capital_expenditure")

        margin = sec["operating_margin_pct"]
        fcf = sec["free_cash_flow"]
        revenue_growth = sec["revenue_growth_pct"]
        name = sec["name"]

        financial_history = []
        rev_hist = {x["end"]: x for x in sec["history"].get("revenue", [])}
        ni_hist = {x["end"]: x for x in sec["history"].get("net_income", [])}
        eps_hist = {x["end"]: x for x in sec["history"].get("eps", [])}
        oi_hist = {x["end"]: x for x in sec["history"].get("operating_income", [])}
        cfo_hist = {x["end"]: x for x in sec["history"].get("operating_cash_flow", [])}
        capex_hist = {x["end"]: x for x in sec["history"].get("capital_expenditure", [])}

        for period_end in sorted(rev_hist.keys(), reverse=True):
            rev = rev_hist[period_end].get("value")
            oi = oi_hist.get(period_end, {}).get("value")
            cfo = cfo_hist.get(period_end, {}).get("value")
            capex = capex_hist.get(period_end, {}).get("value")
            financial_history.append(FinancialPeriod(
                period_end=period_end,
                revenue=rev,
                net_income=ni_hist.get(period_end, {}).get("value"),
                eps=eps_hist.get(period_end, {}).get("value"),
                operating_margin_pct=(100 * oi / rev if rev and oi is not None else None),
                free_cash_flow=(cfo - capex if cfo is not None and capex is not None else None),
            ))
    else:
        revenue = net_income = eps = margin = fcf = revenue_growth = None
        name = ticker
        financial_history = []
        limitations.append("SEC company not found or unavailable; financial fields are not simulated.")
        evidence.append(Evidence(
            id="sec-unavailable",
            source_kind="sec",
            title="SEC company facts",
            fact_or_inference="missing",
            summary="No verified SEC financial statement available.",
        ))

    av = AlphaVantageProvider()
    try:
        overview = await av.query("OVERVIEW", ticker)
    except Exception as exc:
        overview = {}
        limitations.append(f"Market overview unavailable: {type(exc).__name__}.")
    if overview.get("_missing_key"):
        limitations.append("ALPHA_VANTAGE_API_KEY not configured; market capitalization unavailable.")

    def market_number(key):
        try:
            value = float(overview[key])
            return value if value > 0 else None
        except (KeyError, ValueError, TypeError):
            return None

    market_cap = market_number("MarketCapitalization")
    evidence.append(Evidence(
        id="av-overview",
        source_kind="market",
        title="Alpha Vantage company overview",
        url="https://www.alphavantage.co/documentation/",
        fact_or_inference="fact" if market_cap else "missing",
        summary="Market capitalization is vendor-sourced, if available; check quote freshness before investment use.",
    ))

    scenarios = []
    if revenue is not None and revenue > 0 and margin is not None:
        for label, growth, assumed_margin, multiple in [
            ("Bull", 25, 35, 24),
            ("Base", 15, 30, 20),
            ("Bear", 5, 23, 14),
        ]:
            scenarios.append(Scenario(
                name=label,
                revenue_growth_pct=growth,
                operating_margin_pct=assumed_margin,
                exit_multiple=multiple,
                implied_value=scenario_value(revenue, growth, assumed_margin, multiple),
            ))
        limitations.append("Scenario assumptions are illustrative; implied values are not share-price targets or a DCF.")
    else:
        limitations.append("Scenarios withheld: verified SEC revenue and operating margin are required.")

    limitations.append("Management Tone Index withheld until actual attributable earnings transcripts are ingested.")
    limitations.append("SEC history is annual FY data; quarterly point-in-time modeling is a later pipeline stage.")

    thesis = [
        "Verified annual SEC fundamentals are displayed when available.",
        "Revenue growth is calculated only from consecutive verified annual SEC observations.",
        "Scenario assumptions are illustrative and require independent underwriting.",
    ]
    catalysts = []
    risks = []
    if revenue_growth is not None:
        catalysts.append(f"Verified annual revenue growth: {revenue_growth:.1f}%." if revenue_growth >= 0 else
                         f"Revenue contracted {abs(revenue_growth):.1f}% year over year.")
    if margin is not None and margin > 0:
        catalysts.append(f"Latest verified operating margin: {margin:.1f}%.")
    if margin is not None and margin < 0:
        risks.append(f"Latest verified operating margin is negative at {margin:.1f}%.")
    risks.append("Market valuation, forward estimates, and current news are incomplete without configured market/news providers.")

    return ResearchReport(
        ticker=ticker,
        mode="sec_evidence_first",
        generated_at=datetime.now(timezone.utc).isoformat(),
        company={
            "symbol": ticker,
            "name": name,
            "description": overview.get("Description") or "No verified description available.",
        },
        financials=FinancialSnapshot(
            revenue=revenue,
            revenue_growth_pct=revenue_growth,
            net_income=net_income,
            eps=eps,
            operating_margin_pct=margin,
            free_cash_flow=fcf,
            market_cap=market_cap,
        ),
        financial_history=financial_history,
        tone=ToneAnalysis(),
        scenarios=scenarios,
        thesis=thesis,
        catalysts=catalysts,
        risks=risks,
        limitations=limitations,
        evidence=evidence,
    )
