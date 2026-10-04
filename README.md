# AI Investment Research Analyst

> Evidence-first AI research infrastructure for public equities.

The **AI Investment Research Analyst** turns a public-company ticker into a structured, evidence-backed equity research workflow.

## Product Vision

The target workflow is:

~~~text
Ticker
  ↓
Company Identity
  ↓
Primary / Market Data Collection
  ↓
Financial Normalization
  ↓
Valuation
  ↓
Earnings Transcript NLP
  ↓
Management Tone Index
  ↓
Growth / Risk / Competitive Analysis
  ↓
Bull / Base / Bear Scenarios
  ↓
Investment Thesis
  ↓
Evidence Ledger
  ↓
Research Brief
~~~

### Core principle

**The AI interprets evidence; it does not invent financial facts.**

---

## Architecture

~~~text
                    AI INVESTMENT RESEARCH ANALYST
                               │
                           Enter Ticker
                               │
             ┌─────────────────┴─────────────────┐
             │                                   │
       PRIMARY DATA                       MARKET INTELLIGENCE
             │                                   │
       SEC / XBRL                         Price / Volume
       Company Filings                    Earnings
       Financials                         News
       Guidance                           Macro
             │                                   │
             └─────────────────┬─────────────────┘
                               │
                         RESEARCH ENGINE
                               │
              ┌────────────────┼────────────────┐
              │                │                │
          Financials       Valuation       Earnings NLP
              │                │                │
           Growth          Scenarios          Sentiment
           Margins          Multiples         Topics
           FCF              DCF*              Guidance
           Leverage         Comps*            Tone
              │                │                │
              └────────────────┼────────────────┘
                               │
                    MANAGEMENT TONE INDEX
                               │
                      Current vs Previous
                               │
                               ▼
                         THESIS ENGINE
                               │
                    ┌──────────┼──────────┐
                    │          │          │
                   Bull       Base       Bear
                    │          │          │
                    └──────────┼──────────┘
                               │
                               ▼
                        EVIDENCE LEDGER
                               │
                               ▼
                         RESEARCH UI

* Planned modules
~~~

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js / React |
| Backend | FastAPI / Python |
| Quantitative Engine | Python |
| NLP Engine | Python |
| Financial Data | Alpha Vantage |
| Primary Filings | SEC EDGAR |
| Macro Data | FRED |
| AI Layer | OpenAI structured synthesis — planned |
| CI | GitHub Actions |
| Deployment Target | Vercel + server-side API |
| Persistence | Supabase — planned |

---

## Current Implementation

### FastAPI Research API

**GET /health**

~~~json
{"status":"healthy"}
~~~

**POST /research**

Request:

~~~json
{"ticker":"NVDA"}
~~~

The endpoint returns:

- company information
- financial snapshot
- management tone
- scenario valuation
- thesis
- catalysts
- risks
- limitations
- evidence records

### Data Providers

#### SEC EDGAR
Primary-source foundation for company filings and XBRL financial data.

#### Alpha Vantage
Current adapter supports company overview, earnings, and news/sentiment requests.

#### FRED
Macro provider foundation for rates, inflation, GDP, employment, and other economic series.

---

# Management Tone Index

The project includes an experimental **Management Tone Index (MTI)**.

~~~text
MTIₜ = Σ(wᵢ × Sentimentᵢ) / Σwᵢ
~~~

Where:

- Sentimentᵢ = sentence sentiment
- wᵢ = sentence importance weight

Higher weights are currently applied to:

- management guidance
- revenue commentary
- growth commentary
- profitability / margin commentary

Quarter-over-quarter change:

~~~text
ΔMTI = MTIₜ - MTIₜ₋₁
~~~

The current transcript is a deterministic development fixture and is explicitly labeled as such. It is **not** treated as a standalone investment signal.

---

# NLP Pipeline

~~~text
Transcript
   ↓
Sentence Segmentation
   ↓
Sentiment
   ↓
Topic Classification
   ↓
Guidance Detection
   ↓
Importance Weighting
   ↓
MTI
   ↓
Quarter-over-Quarter Comparison
~~~

Current topic classes:

- Growth
- Profitability
- Capital allocation
- Competition
- Macro / regulatory
- General

Planned NLP improvements:

- financial entity recognition
- KPI extraction
- guidance extraction
- demand commentary
- pricing commentary
- capacity commentary
- capex commentary
- hiring commentary
- capital allocation commentary
- geopolitical exposure
- regulatory exposure
- contradiction detection
- management-language change detection

---

# Scenario Engine

Current development scenarios:

| Scenario | Growth | Margin | Exit Multiple |
|---|---:|---:|---:|
| Bull | 25% | 35% | 24x |
| Base | 15% | 30% | 20x |
| Bear | 5% | 23% | 14x |

Current model:

~~~text
Forward Revenue
    ×
Operating Margin
    ×
Exit Multiple
    =
Implied Operating Value
~~~

These are **model-derived scenario outputs**, not target prices.

Planned valuation modules:

- DCF
- WACC
- terminal value
- sensitivity matrices
- trading comparables
- EV / Revenue
- EV / EBITDA
- P / E
- FCF yield
- enterprise-value bridge
- consensus-vs-model bridge

---

# Evidence-First Research Model

Every material research item should eventually retain:

| Field | Purpose |
|---|---|
| Source ID | Traceability |
| Source Type | SEC / market / news / transcript / model |
| As-of Date | Point-in-time discipline |
| Fact Type | Fact / company claim / estimate / inference |
| Summary | Human-readable evidence |
| URL | Source navigation |
| Confidence | Evidence quality |
| Research Status | Verified / pending / conflicting |

The system explicitly separates:

**Facts** — directly sourced financial or market information.

**Company Claims** — statements made by management.

**Estimates** — Street or analyst estimates.

**Model-Derived Values** — quantitative outputs generated by the project.

**Inference** — analyst or AI interpretation derived from evidence.

---

# Frontend

The current analyst interface provides:

- ticker search
- company overview
- financial snapshot
- Management Tone Index
- scenario analysis
- transcript sentence ledger
- catalysts
- risks
- evidence ledger
- research limitations

The UI is designed as a research terminal rather than a generic chatbot.

---

# Repository Structure

~~~text
AI-Investment-Research-Analyst/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── providers.py
│   │   ├── research.py
│   │   ├── nlp.py
│   │   └── valuation.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── app/
│   │   ├── layout.js
│   │   ├── page.js
│   │   └── globals.css
│   └── package.json
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .env.example
├── .gitignore
└── README.md
~~~

---

# Local Development

## Backend

~~~bash
cd backend
python -m venv .venv
~~~

Windows:

~~~bash
.venv\Scripts\activate
~~~

macOS / Linux:

~~~bash
source .venv/bin/activate
~~~

Install:

~~~bash
pip install -r requirements.txt
uvicorn app.main:app --reload
~~~

API:

~~~text
http://localhost:8000
~~~

## Frontend

~~~bash
cd frontend
npm install
npm run dev
~~~

Frontend:

~~~text
http://localhost:3000
~~~

---

# Environment Variables

Create a local .env file from .env.example:

~~~env
ALPHA_VANTAGE_API_KEY=
FRED_API_KEY=
OPENAI_API_KEY=
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
~~~

**Never commit API keys to GitHub.**

---

# CI

GitHub Actions currently validates:

- Python dependency installation
- backend Python compilation
- Node.js dependency installation
- Next.js production build

Pipeline:

~~~text
Push / Pull Request
        ↓
GitHub Actions
        ↓
Backend validation
        +
Frontend build
~~~

---

# Roadmap

## Phase 1 — Foundation

**Implemented**

- [x] FastAPI backend
- [x] Next.js frontend
- [x] Research endpoint
- [x] Alpha Vantage adapter
- [x] SEC adapter foundation
- [x] FRED adapter foundation
- [x] Evidence schema
- [x] Scenario engine
- [x] NLP baseline
- [x] Management Tone Index
- [x] GitHub Actions CI

## Phase 2 — Real Financial Research

- [ ] SEC company identity resolver
- [ ] SEC XBRL financial ingestion
- [ ] Historical income statements
- [ ] Balance sheet normalization
- [ ] Cash-flow normalization
- [ ] Revenue growth
- [ ] Gross margin
- [ ] Operating margin
- [ ] FCF
- [ ] ROIC
- [ ] Net debt
- [ ] Diluted shares
- [ ] Point-in-time financial snapshots

## Phase 3 — Institutional Valuation

- [ ] DCF engine
- [ ] WACC
- [ ] Terminal value
- [ ] Sensitivity matrices
- [ ] Trading comparables
- [ ] EV / Revenue
- [ ] EV / EBITDA
- [ ] P / E
- [ ] FCF yield
- [ ] Enterprise-value bridge
- [ ] Bull / Base / Bear valuation
- [ ] Consensus-vs-model bridge

## Phase 4 — Earnings Intelligence

- [ ] Real transcript ingestion
- [ ] Quarter identification
- [ ] Speaker segmentation
- [ ] Management vs analyst questions
- [ ] KPI extraction
- [ ] Guidance extraction
- [ ] Guidance changes
- [ ] Management-tone history
- [ ] MTI quarter-over-quarter chart
- [ ] Topic-level tone changes
- [ ] Contradiction detection

## Phase 5 — AI Research Analyst

The AI layer will operate **after** evidence collection and quantitative analysis.

~~~text
Structured Evidence
       ↓
Quantitative Results
       ↓
Transcript Findings
       ↓
News / Macro Context
       ↓
AI Reasoning
       ↓
Structured Research Claims
       ↓
Cited Research Brief
~~~

Target claim structure:

~~~json
{
  "claim": "Margin expansion is becoming a larger contributor to the base case.",
  "type": "inference",
  "evidence": [
    "financial_history_q4",
    "management_guidance_q4"
  ],
  "confidence": 0.82
}
~~~

The model should never manufacture unsupported revenue, EPS, valuation, guidance, or market-price figures.

## Phase 6 — Research Terminal

Planned modules:

- company overview
- historical financials
- valuation
- DCF
- comps
- earnings intelligence
- management tone history
- market intelligence
- macro exposure
- investment thesis
- catalysts
- risks
- evidence ledger
- thesis tracking

---

# Research Quality Principles

### 1. Evidence before narrative
Do not generate the thesis first and search for evidence afterward.

### 2. Primary sources first
SEC filings, company releases, earnings materials, and trusted market-data providers take priority.

### 3. Point-in-time discipline
Historical research should use information that was actually available at the relevant date.

### 4. Facts ≠ estimates ≠ inference
These must remain separate throughout the pipeline.

### 5. Models are transparent
Valuation assumptions should be inspectable.

### 6. AI is an interpretation layer
The AI should synthesize evidence rather than become the financial database.

### 7. Missing data is acceptable
A missing number should appear as missing rather than being guessed.

### 8. Every thesis should be falsifiable
The system should identify:

- what must be true
- what could invalidate the thesis
- which KPI matters
- which catalyst matters
- what the market may already price in

---

# Current Status

**Version:** 0.1.0-foundation

### Implemented

- Research API
- Next.js analyst UI
- Data-provider architecture
- Evidence schema
- Scenario engine
- NLP baseline
- Management Tone Index
- CI pipeline

### Not yet production-ready

- Live transcript ingestion
- Full SEC/XBRL normalization
- Historical point-in-time database
- Full DCF
- Comparable-company analysis
- Consensus estimates bridge
- Production OpenAI synthesis
- Authentication
- Research persistence
- Thesis tracking
- Automated monitoring

The current release is therefore a **research-engine foundation**, not a production investment advisory system.

---

# Disclaimer

This project is intended for **research, experimentation, software development, and educational purposes**.

It does not constitute personalized investment advice, a recommendation to buy or sell securities, or a substitute for professional financial analysis.

All model-derived outputs should be independently reviewed before being used for investment decisions.
