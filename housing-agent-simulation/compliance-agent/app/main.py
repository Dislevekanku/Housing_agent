from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from app.models import (
    ToolListResponse, CheckComplianceInput, CheckComplianceOutput,
    A2AEnvelope, A2AReceipt, TrustInfo
)
from app.mcp_tools import list_mcp_tools
from app.compliance_checker import ComplianceChecker
from app.settings import settings
from app.trust_logger import trust_logger

app = FastAPI(title="Compliance Agent", version=settings.SERVICE_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

checker = ComplianceChecker()
AGENT_NAME = "compliance"

@app.get("/health")
def health():
    return {"status": "ok", "service": "compliance-agent", "version": settings.SERVICE_VERSION}

@app.get("/mcp/tools", response_model=ToolListResponse)
def mcp_tools():
    return {"tools": [t.model_dump() for t in list_mcp_tools()]}

@app.post("/mcp/invoke/check_compliance", response_model=CheckComplianceOutput)
def invoke_check_compliance(payload: CheckComplianceInput):
    try:
        result = checker.check_compliance(payload)
        
        # Log to trust/provenance and update trust info
        output_dict = result.model_dump()
        trust_metadata = trust_logger.log_action(
            agent=AGENT_NAME,
            action="check_compliance",
            input_ref=f"parcel:{payload.parcel_id}",
            output=output_dict
        )
        
        # Update trust info in result
        result.trust = TrustInfo(**trust_metadata)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
