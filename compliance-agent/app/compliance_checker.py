"""
Compliance Checker Service

Evaluates zoning and code compliance for parcels.
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from app.models import CheckComplianceInput, CheckComplianceOutput, CodeFlag, TrustInfo
from app.settings import settings


class ComplianceChecker:
    def __init__(self):
        self.zoning_rules = self._load_json(settings.ZONING_RULES_PATH)
        self.code_policies = self._load_json(settings.CODE_POLICIES_PATH)
    
    def _load_json(self, path: str) -> Dict[str, Any]:
        """Load JSON file"""
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def check_compliance(self, input_data: CheckComplianceInput) -> CheckComplianceOutput:
        """
        Check zoning and code compliance for a parcel
        """
        zone_rules = self.zoning_rules.get(input_data.zone, {})
        use_rules = zone_rules.get(input_data.proposed_use, {})
        
        # Check zoning compliance
        min_lot_sqft = use_rules.get("min_lot_sqft", 0)
        zoning_pass = input_data.lot_sqft >= min_lot_sqft
        
        # Check code policies
        code_flags = []
        
        # Parking ratio check
        parking_ratio = self.code_policies.get("parking_ratio", {})
        if input_data.proposed_use in parking_ratio:
            ratio = parking_ratio[input_data.proposed_use]
            code_flags.append(CodeFlag(
                policy="parking_ratio",
                detail=f"{ratio} per unit; estimate units to verify"
            ))
        
        # ADA access (always required)
        if self.code_policies.get("ada_access", {}).get("required"):
            code_flags.append(CodeFlag(
                policy="ada_access",
                detail="ADA accessibility compliance required"
            ))
        
        # Egress (always required)
        if self.code_policies.get("egress", {}).get("required"):
            code_flags.append(CodeFlag(
                policy="egress",
                detail="Adequate egress routes required"
            ))
        
        # Generate summary
        if zoning_pass:
            summary = f"Meets {input_data.zone} min lot ({min_lot_sqft} sqft). Review parking ratio at site plan."
        else:
            summary = f"FAILS {input_data.zone} min lot requirement ({min_lot_sqft} sqft required, {input_data.lot_sqft} sqft provided)."
        
        return CheckComplianceOutput(
            parcel_id=input_data.parcel_id,
            zoning_pass=zoning_pass,
            code_flags=code_flags,
            summary=summary,
            trust=TrustInfo(signed_by="compliance-agent", sig="", facts_id="")  # Will be filled by trust_logger
        )
