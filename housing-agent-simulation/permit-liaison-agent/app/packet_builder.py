"""
Permit Packet Builder Service

Assembles permit-readiness packets from parcel and compliance data.
"""
from typing import List
from app.models import PreparePacketInput, PreparePacketOutput, PermitPacket, TrustInfo


class PacketBuilder:
    def build_packet(self, input_data: PreparePacketInput) -> PreparePacketOutput:
        """
        Build a permit-readiness packet from parcel and compliance data
        """
        # Only create packet if compliance passed
        if not input_data.compliance.zoning_pass:
            raise ValueError(f"Cannot create packet for {input_data.parcel_id}: zoning compliance failed")
        
        # Build checklist based on zone and compliance flags
        checklist = ["Zoning determination"]
        
        # Add items based on compliance flags
        flag_policies = [flag.get("policy", "") for flag in input_data.compliance.code_flags]
        if "parking_ratio" in flag_policies:
            checklist.append("Prelim site plan")
            checklist.append("Parking study")
        if "ada_access" in flag_policies:
            checklist.append("ADA accessibility plan")
        if "egress" in flag_policies:
            checklist.append("Egress plan review")
        
        # Generate attachments
        attachments = [
            "zoning_summary.pdf",
            "compliance.json"
        ]
        
        # Determine routing based on zone type
        routing = []
        if input_data.zone.startswith("R-"):
            routing = ["Planning", "ISD"]
        elif input_data.zone.startswith("CC-") or input_data.zone.startswith("MR-"):
            routing = ["Planning", "ISD", "Zoning Board"]
        else:
            routing = ["Planning", "ISD"]
        
        # Estimate timeline (days)
        base_days = 14
        if len(input_data.compliance.code_flags) > 2:
            base_days += 7
        if "Zoning Board" in routing:
            base_days += 7
        
        packet = PermitPacket(
            checklist=checklist,
            attachments=attachments,
            routing=routing,
            estimated_timeline_days=base_days
        )
        
        return PreparePacketOutput(
            parcel_id=input_data.parcel_id,
            packet=packet,
            trust=TrustInfo(signed_by="permit-liaison", sig="", facts_id="")  # Will be filled by trust_logger
        )
