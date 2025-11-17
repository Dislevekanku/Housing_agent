import math
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import (
    ToolListResponse,
    FindCandidatesInput,
    FindCandidatesOutput,
    FindCandidatesMetadata,
    Candidate,
    A2AEnvelope,
    A2AReceipt,
)
from app.mcp_tools import list_mcp_tools
from app.services.zoning_index import ZoningIndex
from app.services.scoring import score_candidates
from app.settings import settings
from app.trust_logger import trust_logger

app = FastAPI(title="Data Scout Agent", version=settings.SERVICE_VERSION)

# CORS for local development (Next.js on localhost:3000/3001)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Dev: allow all origins
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

zindex = ZoningIndex()
AGENT_NAME = "data-scout"

@app.get("/health")
def health():
    return {"status": "ok", "service": "data-scout-agent", "version": settings.SERVICE_VERSION}

@app.get("/mcp/tools", response_model=ToolListResponse)
def mcp_tools():
    return {"tools": [t.model_dump() for t in list_mcp_tools()]}

@app.post("/mcp/invoke/find_candidates", response_model=FindCandidatesOutput)
def invoke_find_candidates(payload: FindCandidatesInput):
    max_results = payload.max_results or settings.MAX_RESULTS

    min_vacancy = (
        payload.min_vacancy
        if payload.min_vacancy is not None
        else settings.DEFAULT_MIN_VACANCY
    )
    min_transit = (
        payload.min_transit
        if payload.min_transit is not None
        else settings.DEFAULT_MIN_TRANSIT
    )

    try:
        df, total_available = zindex.find_candidates(
            allowable_use=payload.allowable_use,
            min_lot_sqft=payload.min_lot_sqft,
            min_vacancy=min_vacancy,
            min_transit=min_transit,
            max_results=max_results,
        )

        lot_baseline = payload.min_lot_sqft if payload.min_lot_sqft else None
        if lot_baseline is None:
            if "lot_sqft" in df and not df["lot_sqft"].empty:
                lot_baseline = df["lot_sqft"].max()
        if not lot_baseline or (isinstance(lot_baseline, float) and math.isnan(lot_baseline)):
            lot_baseline = 1.0
        df_scored = score_candidates(
            df,
            weights=settings.SCORE_WEIGHTS,
            lot_norm_baseline=lot_baseline,
        )

        results = []
        for idx, r in df_scored.iterrows():
            allowable_uses_list = r.get("allowable_uses_list") or []
            results.append(
                Candidate(
                    parcel_id=str(r.get("parcel_id", "")),
                    address=r.get("address"),
                    zoning_district=r.get("zoning_district"),
                    score=float(r.get("score", 0.0)),
                    lot_sqft=float(r.get("lot_sqft", 0.0))
                    if r.get("lot_sqft") is not None
                    else None,
                    allowable_uses=allowable_uses_list,
                    vacancy_signal=float(r.get("vacancy_signal"))
                    if r.get("vacancy_signal") is not None
                    else None,
                    transit_score=float(r.get("transit_score"))
                    if r.get("transit_score") is not None
                    else None,
                    provenance=f"file://{zindex.path}#row={idx}",
                )
            )

        max_score = (
            float(df_scored["score"].max()) if not df_scored.empty else None
        )
        metadata = FindCandidatesMetadata(
            total_available=total_available,
            returned=len(results),
            max_score=max_score,
            filters={
                "allowable_use": payload.allowable_use,
                "min_lot_sqft": payload.min_lot_sqft,
                "min_vacancy": min_vacancy,
                "min_transit": min_transit,
                "max_results": max_results,
            },
            dataset_hash=zindex.dataset_hash,
        )

        # Log to shared trust/provenance ledger
        output_dict: Dict[str, Any] = {
            "results": [r.model_dump() for r in results],
            "metadata": metadata.model_dump(),
        }
        trust_metadata = trust_logger.log_action(
            agent=AGENT_NAME,
            action="find_candidates",
            input_ref=f"query:{payload.allowable_use}",
            output=output_dict,
        )
        
        # Store facts_id in each candidate for chain validation
        facts_id = trust_metadata.get("facts_id")
        for r in results:
            r.facts_id = facts_id

        return FindCandidatesOutput(results=results, metadata=metadata)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/data/refresh")
def refresh_dataset():
    """Reload parcel data from disk"""
    try:
        zindex.refresh()
        trust_logger.log_action(
            agent=AGENT_NAME,
            action="refresh_dataset",
            input_ref="dataset:parcels",
            output={"dataset_hash": zindex.dataset_hash},
        )
        return {
            "status": "ok",
            "dataset_hash": zindex.dataset_hash,
            "refreshed_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/a2a", response_model=A2AReceipt)
def receive_a2a_message(envelope: A2AEnvelope):
    """Receive A2A message from another agent"""
    try:
        # Log receipt
        receipt = A2AReceipt(
            msg_id=envelope.msg_id,
            received_at=datetime.now(timezone.utc).isoformat(),
            status="received",
            agent=AGENT_NAME
        )
        
        # Log to provenance
        trust_logger.log_action(
            agent=AGENT_NAME,
            action="a2a_receive",
            input_ref=f"msg_id:{envelope.msg_id}",
            output={"from": envelope.from_agent, "payload_keys": list(envelope.payload.keys())}
        )
        
        return receipt
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
