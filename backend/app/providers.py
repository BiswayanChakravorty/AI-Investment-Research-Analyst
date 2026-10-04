import os
import httpx

SEC_HEADERS = {"User-Agent": "AI-Investment-Research-Analyst/0.1 research@example.com"}

class SECProvider:
    async def company_submissions(self, cik: str) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json", headers=SEC_HEADERS)
            response.raise_for_status()
            return response.json()

class AlphaVantageProvider:
    def __init__(self) -> None:
        self.key = os.getenv("ALPHA_VANTAGE_API_KEY")

    async def query(self, function: str, symbol: str) -> dict:
        if not self.key:
            return {"_missing_key": True, "function": function, "symbol": symbol}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get("https://www.alphavantage.co/query", params={"function": function, "symbol": symbol, "apikey": self.key})
            response.raise_for_status()
            return response.json()

class FREDProvider:
    def __init__(self) -> None:
        self.key = os.getenv("FRED_API_KEY")

    async def observations(self, series_id: str, limit: int = 8) -> dict:
        if not self.key:
            return {"_missing_key": True, "series_id": series_id}
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get("https://api.stlouisfed.org/fred/series/observations", params={"series_id": series_id, "api_key": self.key, "file_type": "json", "sort_order": "desc", "limit": limit})
            response.raise_for_status()
            return response.json()
