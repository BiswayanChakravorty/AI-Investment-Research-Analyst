from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import ResearchRequest,ResearchReport
from .research import build_research_report
app=FastAPI(title="AI Investment Research Analyst API",version="0.1.0")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
@app.get("/")
def root(): return {"service":"AI Investment Research Analyst API","status":"ok"}
@app.get("/health")
def health(): return {"status":"healthy"}
@app.post("/research",response_model=ResearchReport)
async def research(request:ResearchRequest):
    try:return await build_research_report(request.ticker.upper().strip())
    except ValueError as e:raise HTTPException(status_code=400,detail=str(e))
    except Exception as e:raise HTTPException(status_code=502,detail=f"Research pipeline failed: {e}")
