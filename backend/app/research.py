from datetime import datetime,timezone
from .providers import AlphaVantageProvider
from .nlp import analyze_transcript,compare_tone
from .valuation import scenario_value
from .models import ResearchReport,FinancialSnapshot,Scenario,Evidence
DEMO_CURRENT="We are seeing strong demand and expect revenue growth to remain healthy. Margins should improve as capacity utilization increases. Competition remains intense, but our differentiation is robust. We anticipate elevated capex to support AI infrastructure. We remain confident in the long-term opportunity."
DEMO_PRIOR="Demand was solid and we expected growth to continue. Margins faced some pressure from capacity investments. Competition remained intense. We planned higher capex as customer demand improved."
async def build_research_report(ticker):
    if not ticker.isalpha(): raise ValueError("Ticker must contain alphabetic characters only.")
    av=AlphaVantageProvider(); overview=await av.query("OVERVIEW",ticker); earnings=await av.query("EARNINGS",ticker); news=await av.query("NEWS_SENTIMENT",ticker)
    def number(k):
        try:return float(overview.get(k))
        except (TypeError,ValueError):return None
    revenue=number("RevenueTTM"); market_cap=number("MarketCapitalization"); eps=number("EPS")
    tone=compare_tone(analyze_transcript(DEMO_CURRENT),analyze_transcript(DEMO_PRIOR)); base=revenue or 100_000_000_000
    scenarios=[Scenario("Bull",25,35,24,scenario_value(base,25,35,24)),Scenario("Base",15,30,20,scenario_value(base,15,30,20)),Scenario("Bear",5,23,14,scenario_value(base,5,23,14))]
    evidence=[Evidence(id="av-overview",source_kind="market",title="Alpha Vantage company overview",fact_or_inference="fact" if "_missing_key" not in overview else "missing",summary="Company fundamentals requested from Alpha Vantage."),Evidence(id="av-earnings",source_kind="market",title="Alpha Vantage earnings",fact_or_inference="fact" if "_missing_key" not in earnings else "missing",summary="Historical earnings data requested from Alpha Vantage."),Evidence(id="av-news",source_kind="news",title="Alpha Vantage news and sentiment",fact_or_inference="fact" if "_missing_key" not in news else "missing",summary="Recent news and sentiment feed requested from Alpha Vantage."),Evidence(id="transcript-demo",source_kind="transcript",title="Deterministic transcript fixture",fact_or_inference="fact",summary="Demo-only transcript fixture used to exercise the NLP pipeline.")]
    return ResearchReport(ticker=ticker,mode="evidence_first_demo",generated_at=datetime.now(timezone.utc).isoformat(),company={"symbol":ticker,"name":overview.get("Name") or ticker,"description":overview.get("Description") or "No live company description available."},financials=FinancialSnapshot(revenue=revenue,market_cap=market_cap,eps=eps),tone=tone,scenarios=scenarios,thesis=["Separate sourced facts from model-derived valuation.","Treat management tone as an experimental signal, not a stand-alone investment conclusion.","Next upgrade: real transcript ingestion and point-in-time quarter storage."],catalysts=["Revenue growth re-acceleration","Margin expansion","Positive management guidance"],risks=["Competitive intensity","High capital intensity","Macro or regulatory shocks"],limitations=["Transcript text is a deterministic fixture until a live or licensed transcript source is connected.","Scenario values are model-derived and are not target prices.","Missing API keys intentionally produce incomplete evidence rather than fabricated numbers."],evidence=evidence)
