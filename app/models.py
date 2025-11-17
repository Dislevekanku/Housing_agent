from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Minimal MCP-ish schemas for tools list and invocation
class MCPToolSchema(BaseModel):
    name: str
    description: str
    input_schema: dict
    output_schema: dict

class ToolListResponse(BaseModel):
    tools: List[MCPToolSchema]

class Candidate(BaseModel):
    parcel_id: str
    address: Optional[str] = None
    zoning_district: Optional[str] = None
    score: float
    lot_sqft: Optional[float] = None
    allowable_uses: Optional[List[str]] = None
    vacancy_signal: Optional[float] = None
    transit_score: Optional[float] = None
    provenance: str
    facts_id: Optional[str] = None  # For chain validation

class FindCandidatesInput(BaseModel):
    allowable_use: str = Field(..., description="e.g., residential, mixed-use")
    min_lot_sqft: Optional[float] = Field(None, description="minimum lot size")
    min_vacancy: Optional[float] = Field(
        None, description="minimum vacancy signal (0-1)"
    )
    min_transit: Optional[float] = Field(
        None, description="minimum transit score (0-1)"
    )
    max_results: Optional[int] = Field(None, description="limit results")

class FindCandidatesMetadata(BaseModel):
    total_available: int
    returned: int
    max_score: Optional[float] = None
    filters: Dict[str, Any]
    dataset_hash: Optional[str] = None

class FindCandidatesOutput(BaseModel):
    results: List[Candidate]
    metadata: FindCandidatesMetadata

# A2A Message Envelope
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
    status: str  # "received", "processed", "error"
    agent: str
