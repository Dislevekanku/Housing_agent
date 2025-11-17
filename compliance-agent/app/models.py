from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class MCPToolSchema(BaseModel):
    name: str
    description: str
    input_schema: dict
    output_schema: dict

class ToolListResponse(BaseModel):
    tools: List[MCPToolSchema]

class CheckComplianceInput(BaseModel):
    parcel_id: str
    zone: str
    proposed_use: str
    lot_sqft: float
    parent_facts_id: Optional[str] = None  # For chain validation

class CodeFlag(BaseModel):
    policy: str
    detail: str

class TrustInfo(BaseModel):
    signed_by: str
    sig: str
    facts_id: str

class CheckComplianceOutput(BaseModel):
    parcel_id: str
    zoning_pass: bool
    code_flags: List[CodeFlag]
    summary: str
    trust: TrustInfo

class A2AEnvelope(BaseModel):
    msg_id: str
    from_agent: str = Field(..., alias="from")
    to_agent: str = Field(..., alias="to")
    timestamp: str
    payload: Dict[str, Any]
    proof: Optional[Dict[str, Any]] = None

class A2AReceipt(BaseModel):
    msg_id: str
    received_at: str
    status: str
    agent: str
