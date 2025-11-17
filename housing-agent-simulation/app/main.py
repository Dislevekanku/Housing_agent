from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import uuid
from app.models import (
    ToolListResponse, FindCandidatesInput, FindCandidatesOutput, Candidate,
    A2AEnvelope, A2AReceipt
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
    try:
        df = zindex.find_candidates(
            allowable_use=payload.allowable_use,
            min_lot_sqft=payload.min_lot_sqft,
            max_results=max_results
        )
        df_scored = score_candidates(df)
        results = []
        for idx, r in df_scored.iterrows():
            results.append(Candidate(
                parcel_id=str(r.get("parcel_id", "")),
                address=r.get("address"),
                zoning_district=r.get("zoning_district"),
                score=float(r.get("score", 0.0)),
                provenance=f"file://{zindex.path}#row={idx}"
            ))
        
        # Log to trust/provenance
        output_dict = {"results": [r.model_dump() for r in results]}
        trust_logger.log_action(
            agent=AGENT_NAME,
            action="find_candidates",
            input_ref=f"query:{payload.allowable_use}",
            output=output_dict
        )
        
        return FindCandidatesOutput(results=results)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
