from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class MCPToolSchema(BaseModel):
    name: str
    description: str
    input_schema: dict
    output_schema: dict

class ToolListResponse(BaseModel):
    tools: List[MCPToolSchema]

class ComplianceData(BaseModel):
    parcel_id: str
    zoning_pass: bool
    code_flags: List[Dict[str, str]]
    summary: str
    trust: Dict[str, str]

class PreparePacketInput(BaseModel):
    parcel_id: str
    address: str
    zone: str
    compliance: ComplianceData

class PermitPacket(BaseModel):
    checklist: List[str]
    attachments: List[str]
    routing: List[str]
    estimated_timeline_days: int

class TrustInfo(BaseModel):
    signed_by: str
    sig: str
    facts_id: str

class PreparePacketOutput(BaseModel):
    parcel_id: str
    packet: PermitPacket
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
