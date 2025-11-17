from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from app.models import (
    ToolListResponse, PreparePacketInput, PreparePacketOutput,
    A2AEnvelope, A2AReceipt, TrustInfo
)
from app.mcp_tools import list_mcp_tools
from app.packet_builder import PacketBuilder
from app.settings import settings
from app.trust_logger import trust_logger

app = FastAPI(title="Permit Liaison Agent", version=settings.SERVICE_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

builder = PacketBuilder()
AGENT_NAME = "permit-liaison"

@app.get("/health")
def health():
    return {"status": "ok", "service": "permit-liaison-agent", "version": settings.SERVICE_VERSION}

@app.get("/mcp/tools", response_model=ToolListResponse)
def mcp_tools():
    return {"tools": [t.model_dump() for t in list_mcp_tools()]}

@app.post("/mcp/invoke/prepare_packet", response_model=PreparePacketOutput)
def invoke_prepare_packet(payload: PreparePacketInput):
    try:
        result = builder.build_packet(payload)
        
        # Log to shared trust/provenance ledger with parent chain
        output_dict = result.model_dump()
        # Use parent_facts_id from payload, or extract from compliance output
        parent_facts_id = payload.parent_facts_id
        if not parent_facts_id and hasattr(payload.compliance, 'trust'):
            parent_facts_id = payload.compliance.trust.get("facts_id")
        trust_metadata = trust_logger.log_action(
            agent=AGENT_NAME,
            action="prepare_packet",
            input_ref=f"parcel:{payload.parcel_id}",
            output=output_dict,
            parent_facts_id=parent_facts_id
        )
        
        # Update trust info in result
        result.trust = TrustInfo(**trust_metadata)
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/a2a", response_model=A2AReceipt)
def receive_a2a_message(envelope: A2AEnvelope):
    """Receive A2A message from another agent"""
    try:
        receipt = A2AReceipt(
            msg_id=envelope.msg_id,
            received_at=datetime.now(timezone.utc).isoformat(),
            status="received",
            agent=AGENT_NAME
        )
        
        trust_logger.log_action(
            agent=AGENT_NAME,
            action="a2a_receive",
            input_ref=f"msg_id:{envelope.msg_id}",
            output={"from": envelope.from_agent, "payload_keys": list(envelope.payload.keys())}
        )
        
        return receipt
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
