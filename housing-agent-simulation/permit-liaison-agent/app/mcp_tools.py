from app.models import MCPToolSchema

def mcp_tool_prepare_packet() -> MCPToolSchema:
    return MCPToolSchema(
        name="prepare_packet",
        description="Prepare a permit-readiness packet from parcel and compliance data",
        input_schema={
            "type": "object",
            "properties": {
                "parcel_id": {"type": "string"},
                "address": {"type": "string"},
                "zone": {"type": "string"},
                "compliance": {
                    "type": "object",
                    "properties": {
                        "parcel_id": {"type": "string"},
                        "zoning_pass": {"type": "boolean"},
                        "code_flags": {"type": "array"},
                        "summary": {"type": "string"},
                        "trust": {"type": "object"}
                    }
                }
            },
            "required": ["parcel_id", "address", "zone", "compliance"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "parcel_id": {"type": "string"},
                "packet": {
                    "type": "object",
                    "properties": {
                        "checklist": {"type": "array", "items": {"type": "string"}},
                        "attachments": {"type": "array", "items": {"type": "string"}},
                        "routing": {"type": "array", "items": {"type": "string"}},
                        "estimated_timeline_days": {"type": "integer"}
                    }
                },
                "trust": {
                    "type": "object",
                    "properties": {
                        "signed_by": {"type": "string"},
                        "sig": {"type": "string"},
                        "facts_id": {"type": "string"}
                    }
                }
            },
            "required": ["parcel_id", "packet", "trust"]
        }
    )

def list_mcp_tools():
    return [mcp_tool_prepare_packet()]
