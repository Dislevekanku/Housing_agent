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
                "min_vacancy": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Minimum vacancy threshold (0-1)"
                },
                "min_transit": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Minimum transit score threshold (0-1)"
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
                            "lot_sqft": {"type": "number"},
                            "allowable_uses": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "vacancy_signal": {"type": "number"},
                            "transit_score": {"type": "number"},
                            "provenance": {"type": "string"}
                        },
                        "required": ["parcel_id", "score", "provenance"]
                    }
                },
                "metadata": {
                    "type": "object",
                    "properties": {
                        "total_available": {"type": "integer"},
                        "returned": {"type": "integer"},
                        "max_score": {"type": "number"},
                        "filters": {"type": "object"},
                        "dataset_hash": {"type": "string"}
                    },
                    "required": ["total_available", "returned", "filters"]
                }
            },
            "required": ["results", "metadata"]
        }
    )

def list_mcp_tools():
    return [mcp_tool_find_candidates()]
