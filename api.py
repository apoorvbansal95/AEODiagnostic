import asyncio
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from diagnostic import run_aeo_diagnostic, run_brand_diagnostic, run_multi_query_diagnostic

app = FastAPI(title="AEO Diagnostic API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request Models ---

class BrandDiagnosticRequest(BaseModel):
    target_brand: str
    competitors: List[str]
    queries: List[str]

class SingleQueryRequest(BaseModel):
    query: str

class MultiQueryRequest(BaseModel):
    queries: List[str]
    known_brands: Optional[List[str]] = None

# --- Routes ---

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/diagnostic/query")
async def single_query_diagnostic(request: SingleQueryRequest):
    """
    Run AEO diagnostic for a single user query.
    Returns per-model rankings and cross-model AEO visibility scores.
    """
    try:
        model_results, aeo_scores = await asyncio.to_thread(
            run_aeo_diagnostic, request.query
        )
        return jsonable_encoder({
            "query": request.query,
            "model_rankings": {
                name: [
                    {"rank": r.rank, "brand_name": r.brand_name, "reasoning": r.reasoning}
                    for r in report.recommendations
                ]
                for name, report in model_results.items()
            },
            "aeo_scores": aeo_scores,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/diagnostic/brand")
async def brand_diagnostic(request: BrandDiagnosticRequest):
    """
    Run a full brand-centric AEO diagnostic.
    Returns target brand visibility, competitor comparison, gap analysis,
    and missed queries (AEO opportunities).
    """
    try:
        result = await asyncio.to_thread(
            run_brand_diagnostic,
            request.target_brand,
            request.competitors,
            request.queries,
        )
        return jsonable_encoder(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/diagnostic/multi-query")
async def multi_query_diagnostic(request: MultiQueryRequest):
    """
    Run a multi-query AEO diagnostic without brand targeting.
    Returns per-brand visibility and stability scores across all queries.
    """
    try:
        result = await asyncio.to_thread(
            run_multi_query_diagnostic,
            request.queries,
            request.known_brands,
        )
        return jsonable_encoder(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))