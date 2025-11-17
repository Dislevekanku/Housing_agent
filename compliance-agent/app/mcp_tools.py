from app.models import MCPToolSchema

def mcp_tool_check_compliance() -> MCPToolSchema:
    return MCPToolSchema(
        name="check_compliance",
        description="Check zoning and code compliance for a parcel",
        input_schema={
            "type": "object",
            "properties": {
                "parcel_id": {"type": "string"},
                "zone": {"type": "string"},
                "proposed_use": {"type": "string"},
                "lot_sqft": {"type": "number"}
            },
            "required": ["parcel_id", "zone", "proposed_use", "lot_sqft"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "parcel_id": {"type": "string"},
                "zoning_pass": {"type": "boolean"},
                "code_flags": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "policy": {"type": "string"},
                            "detail": {"type": "string"}
                        }
                    }
                },
                "summary": {"type": "string"},
                "trust": {
                    "type": "object",
                    "properties": {
                        "signed_by": {"type": "string"},
                        "sig": {"type": "string"},
                        "facts_id": {"type": "string"}
                    }
                }
            },
            "required": ["parcel_id", "zoning_pass", "code_flags", "summary", "trust"]
        }
    )

def list_mcp_tools():
    return [mcp_tool_check_compliance()]
