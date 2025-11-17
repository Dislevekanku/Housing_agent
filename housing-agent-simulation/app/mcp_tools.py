from app.models import MCPToolSchema

def mcp_tool_find_candidates() -> MCPToolSchema:
    return MCPToolSchema(
        name="find_candidates",
        description="Return parcels likely convertible to housing.",
        input_schema={
            "type": "object",
            "properties": {
                "min_lot_sqft": {"type": "number"},
                "allowable_use": {
                    "type": "string",
                    "enum": ["residential", "mixed-use", "commercial", "industrial"]
                },
                "max_results": {"type": "integer", "default": 25}
            },
            "required": ["allowable_use"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "parcel_id": {"type": "string"},
                            "address": {"type": "string"},
                            "zoning_district": {"type": "string"},
                            "score": {"type": "number"},
                            "provenance": {"type": "string"}
                        },
                        "required": ["parcel_id", "score", "provenance"]
                    }
                }
            },
            "required": ["results"]
        }
    )

def list_mcp_tools():
    return [mcp_tool_find_candidates()]
