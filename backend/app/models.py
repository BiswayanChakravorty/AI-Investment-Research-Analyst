from pydantic import BaseModel, Field
from typing import Literal, Optional
SourceKind = Literal["sec","market","macro","news","transcript","model"]
FactType = Literal["fact","company_claim","estimate","model_derived","inference","missing"]
class ResearchRequest(BaseModel):
    ticker: str = Field(min_length=1,max_length=12)
class Evidence(BaseModel):
    id: str; source_kind: SourceKind; title: str; as_of: Optional[str]=None; url: Optional[str]=None; fact_or_inference: FactType; summary: str
class FinancialSnapshot(BaseModel):
    revenue: Optional[float]=None; revenue_growth_pct: Optional[float]=None; net_income: Optional[float]=None; eps: Optional[float]=None; gross_margin_pct: Optional[float]=None; operating_margin_pct: Optional[float]=None; free_cash_flow: Optional[float]=None; market_cap: Optional[float]=None
class ToneSentence(BaseModel):
    text: str; sentiment: float; topic: str; guidance: bool; weight: float
class ToneAnalysis(BaseModel):
    current_mti: Optional[float]=None; prior_mti: Optional[float]=None; delta_mti: Optional[float]=None; sentences: list[ToneSentence]=[]
class Scenario(BaseModel):
    name: str; revenue_growth_pct: float; operating_margin_pct: float; exit_multiple: float; implied_value: float
class ResearchReport(BaseModel):
    ticker: str; mode: str; generated_at: str; company: dict; financials: FinancialSnapshot; tone: ToneAnalysis; scenarios: list[Scenario]; thesis: list[str]; catalysts: list[str]; risks: list[str]; limitations: list[str]; evidence: list[Evidence]
