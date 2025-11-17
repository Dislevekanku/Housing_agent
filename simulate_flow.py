#!/usr/bin/env python3
"""
Simulation Runner for Zoning → Permit Data Flow

Orchestrates the end-to-end flow:
1. Data Scout finds candidates
2. Compliance checks zoning/code
3. Permit Liaison assembles packet
"""
import json
import uuid
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
import sys

try:
    import requests
except ImportError:
    print("ERROR: requests library not installed. Run: pip install requests")
    sys.exit(1)


# Agent endpoints (default to localhost)
DATA_SCOUT_URL = "http://localhost:8000"
COMPLIANCE_URL = "http://localhost:8001"
PERMIT_LIAISON_URL = "http://localhost:8002"

# Artifacts directory
ARTIFACTS_DIR = Path("artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True)


class FlowSimulator:
    def __init__(self):
        self.metrics = {
            "start_time": None,
            "end_time": None,
            "latencies": {},
            "a2a_deliveries": [],
            "errors": []
        }
    
    def send_a2a_message(
        self,
        from_agent: str,
        to_agent: str,
        payload: Dict[str, Any],
        agent_url: str
    ) -> Optional[Dict[str, Any]]:
        """Send A2A message envelope to an agent"""
        envelope = {
            "msg_id": str(uuid.uuid4()),
            "from": from_agent,
            "to": to_agent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
            "proof": {
                "sig": "mock_sig",
                "key_id": f"did:nanda:{from_agent}#1"
            }
        }
        
        start = time.time()
        try:
            response = requests.post(
                f"{agent_url}/a2a",
                json=envelope,
                timeout=10
            )
            latency = (time.time() - start) * 1000  # ms
            self.metrics["latencies"][f"a2a_{from_agent}_to_{to_agent}"] = latency
            
            if response.status_code == 200:
                receipt = response.json()
                self.metrics["a2a_deliveries"].append({
                    "msg_id": envelope["msg_id"],
                    "status": "success",
                    "latency_ms": latency
                })
                return receipt
            else:
                self.metrics["errors"].append(f"A2A failed: {response.status_code}")
                return None
        except Exception as e:
            self.metrics["errors"].append(f"A2A error: {str(e)}")
            return None
    
    def find_candidates(self, allowable_use: str, min_lot_sqft: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Call Data Scout to find candidates"""
        print(f"\n[1] Data Scout: Finding candidates (use: {allowable_use})...")
        start = time.time()
        
        payload = {
            "allowable_use": allowable_use,
            "max_results": 5
        }
        if min_lot_sqft:
            payload["min_lot_sqft"] = min_lot_sqft
        
        try:
            response = requests.post(
                f"{DATA_SCOUT_URL}/mcp/invoke/find_candidates",
                json=payload,
                timeout=10
            )
            latency = (time.time() - start) * 1000
            self.metrics["latencies"]["data_scout_find"] = latency
            
            if response.status_code == 200:
                result = response.json()
                print(f"  [OK] Found {len(result.get('results', []))} candidates")
                return result
            else:
                print(f"  [FAIL] Error: {response.status_code}")
                self.metrics["errors"].append(f"Data Scout: {response.status_code}")
                return None
        except Exception as e:
            print(f"  [FAIL] Error: {e}")
            self.metrics["errors"].append(f"Data Scout: {str(e)}")
            return None
    
    def check_compliance(self, candidate: Dict[str, Any], proposed_use: str, lot_sqft: Optional[float] = None, parent_facts_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Call Compliance Agent to check compliance"""
        parcel_id = candidate.get("parcel_id")
        zone = candidate.get("zoning_district")
        
        print(f"\n[2] Compliance: Checking {parcel_id} ({zone})...")
        start = time.time()
        
        # Get lot_sqft from candidate data if available, otherwise use default
        if not lot_sqft:
            # Try to get from candidate metadata or use default based on test case
            lot_sqft = 7000  # Default for TC-1
        
        payload = {
            "parcel_id": parcel_id,
            "zone": zone,
            "proposed_use": proposed_use,
            "lot_sqft": lot_sqft,
            "parent_facts_id": parent_facts_id  # Pass parent facts_id for chain validation
        }
        
        try:
            response = requests.post(
                f"{COMPLIANCE_URL}/mcp/invoke/check_compliance",
                json=payload,
                timeout=10
            )
            latency = (time.time() - start) * 1000
            self.metrics["latencies"]["compliance_check"] = latency
            
            if response.status_code == 200:
                result = response.json()
                zoning_pass = result.get("zoning_pass", False)
                print(f"  [OK] Zoning pass: {zoning_pass}")
                print(f"  Summary: {result.get('summary', '')}")
                return result
            else:
                print(f"  [FAIL] Error: {response.status_code}")
                self.metrics["errors"].append(f"Compliance: {response.status_code}")
                return None
        except Exception as e:
            print(f"  [FAIL] Error: {e}")
            self.metrics["errors"].append(f"Compliance: {str(e)}")
            return None
    
    def prepare_packet(self, candidate: Dict[str, Any], compliance: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call Permit Liaison to prepare packet"""
        parcel_id = candidate.get("parcel_id")
        
        print(f"\n[3] Permit Liaison: Preparing packet for {parcel_id}...")
        start = time.time()
        
        # Extract parent facts_id from compliance trust info
        parent_facts_id = compliance.get("trust", {}).get("facts_id") if compliance.get("trust") else None
        
        payload = {
            "parcel_id": parcel_id,
            "address": candidate.get("address", ""),
            "zone": candidate.get("zoning_district", ""),
            "compliance": compliance,
            "parent_facts_id": parent_facts_id  # Pass parent facts_id for chain validation
        }
        
        try:
            response = requests.post(
                f"{PERMIT_LIAISON_URL}/mcp/invoke/prepare_packet",
                json=payload,
                timeout=10
            )
            latency = (time.time() - start) * 1000
            self.metrics["latencies"]["permit_prepare"] = latency
            
            if response.status_code == 200:
                result = response.json()
                print(f"  [OK] Packet created")
                print(f"  Timeline: {result['packet']['estimated_timeline_days']} days")
                return result
            else:
                print(f"  [FAIL] Error: {response.status_code}")
                if response.status_code == 400:
                    print(f"  Detail: {response.json().get('detail', '')}")
                self.metrics["errors"].append(f"Permit Liaison: {response.status_code}")
                return None
        except Exception as e:
            print(f"  [FAIL] Error: {e}")
            self.metrics["errors"].append(f"Permit Liaison: {str(e)}")
            return None
    
    def run_test_case(
        self,
        test_name: str,
        allowable_use: str,
        min_lot_sqft: Optional[float] = None,
        proposed_use: Optional[str] = None,
        test_lot_sqft: Optional[float] = None
    ):
        """Run a complete test case"""
        print(f"\n{'='*60}")
        print(f"Test Case: {test_name}")
        print(f"{'='*60}")
        
        self.metrics["start_time"] = datetime.now(timezone.utc).isoformat()
        
        # Step 1: Find candidates
        candidates_result = self.find_candidates(allowable_use, min_lot_sqft)
        if not candidates_result or not candidates_result.get("results"):
            print("  [FAIL] No candidates found")
            return None
        
        candidate = candidates_result["results"][0]  # Take first result
        print(f"  Selected: {candidate.get('address')} ({candidate.get('parcel_id')})")
        
        # Send A2A: Data Scout → Compliance
        self.send_a2a_message(
            "data-scout",
            "compliance",
            {"parcel": candidate},
            COMPLIANCE_URL
        )
        
        # Step 2: Check compliance
        proposed_use = proposed_use or allowable_use
        # Use test_lot_sqft if provided (for TC-2 override), otherwise try to get from candidate
        lot_sqft = test_lot_sqft if test_lot_sqft else None
        # Pass parent facts_id from Data Scout to Compliance for chain validation
        parent_facts_id = candidate.get("facts_id")
        compliance_result = self.check_compliance(candidate, proposed_use, lot_sqft, parent_facts_id)
        if not compliance_result:
            print("  [FAIL] Compliance check failed")
            return None
        
        # Send A2A: Compliance → Permit Liaison
        self.send_a2a_message(
            "compliance",
            "permit-liaison",
            {"compliance": compliance_result},
            PERMIT_LIAISON_URL
        )
        
        # Step 3: Prepare packet (only if compliance passed)
        if compliance_result.get("zoning_pass"):
            packet_result = self.prepare_packet(candidate, compliance_result)
            if not packet_result:
                print("  [FAIL] Packet preparation failed")
                return None
            
            # Save packet to artifacts
            parcel_id = candidate.get("parcel_id")
            parcel_dir = ARTIFACTS_DIR / parcel_id
            parcel_dir.mkdir(exist_ok=True)
            
            packet_file = parcel_dir / "packet.json"
            with open(packet_file, "w", encoding="utf-8") as f:
                json.dump(packet_result, f, indent=2)
            
            print(f"\n  [OK] Packet saved to: {packet_file}")
            
            # Send A2A: Permit Liaison → Data Scout + Compliance (ack)
            self.send_a2a_message(
                "permit-liaison",
                "data-scout",
                {"packet_id": parcel_id, "status": "complete"},
                DATA_SCOUT_URL
            )
            self.send_a2a_message(
                "permit-liaison",
                "compliance",
                {"packet_id": parcel_id, "status": "complete"},
                COMPLIANCE_URL
            )
            
            self.metrics["end_time"] = datetime.now(timezone.utc).isoformat()
            return packet_result
        else:
            print("  [FAIL] Zoning compliance failed - packet not created")
            self.metrics["end_time"] = datetime.now(timezone.utc).isoformat()
            return None
    
    def print_metrics(self):
        """Print metrics summary"""
        print(f"\n{'='*60}")
        print("Metrics Summary")
        print(f"{'='*60}")
        
        if self.metrics["start_time"] and self.metrics["end_time"]:
            start = datetime.fromisoformat(self.metrics["start_time"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(self.metrics["end_time"].replace("Z", "+00:00"))
            total_time = (end - start).total_seconds() * 1000
            print(f"Total Flow Time: {total_time:.2f} ms")
        
        print("\nLatencies (ms):")
        for key, value in self.metrics["latencies"].items():
            print(f"  {key}: {value:.2f}")
        
        print(f"\nA2A Deliveries: {len(self.metrics['a2a_deliveries'])}")
        for delivery in self.metrics["a2a_deliveries"]:
            print(f"  {delivery['msg_id'][:8]}... : {delivery['status']} ({delivery['latency_ms']:.2f} ms)")
        
        if self.metrics["errors"]:
            print(f"\nErrors ({len(self.metrics['errors'])}):")
            for error in self.metrics["errors"]:
                print(f"  - {error}")
        else:
            print("\n[OK] No errors")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simulate zoning → permit data flow")
    parser.add_argument("--test-case", choices=["TC-1", "TC-2", "TC-3", "TC-4"], default="TC-1")
    parser.add_argument("--data-scout-url", default="http://localhost:8000")
    parser.add_argument("--compliance-url", default="http://localhost:8001")
    parser.add_argument("--permit-url", default="http://localhost:8002")
    
    args = parser.parse_args()
    
    # Update global URLs
    global DATA_SCOUT_URL, COMPLIANCE_URL, PERMIT_LIAISON_URL
    DATA_SCOUT_URL = args.data_scout_url
    COMPLIANCE_URL = args.compliance_url
    PERMIT_LIAISON_URL = args.permit_url
    
    simulator = FlowSimulator()
    
    # Test cases
    test_cases = {
        "TC-1": {
            "name": "Happy Path (R-3 residential)",
            "allowable_use": "residential",
            "min_lot_sqft": 6000,
            "proposed_use": "residential",
            "test_lot_sqft": 7000  # PID-103 has 7000, meets R-3 min 6000
        },
        "TC-2": {
            "name": "Fails Min Lot (residential in MR-1, lot 4000)",
            "allowable_use": "residential",
            "min_lot_sqft": 4000,
            "proposed_use": "residential",
            "test_lot_sqft": 4000  # Override to test failure case
        },
        "TC-3": {
            "name": "Mixed-use in CC-2",
            "allowable_use": "mixed-use",
            "min_lot_sqft": 8000,
            "proposed_use": "mixed-use",
            "test_lot_sqft": 12000  # PID-102 has 12000, meets CC-2 min 8000
        },
        "TC-4": {
            "name": "No transit or low vacancy",
            "allowable_use": "residential",
            "min_lot_sqft": 5000,
            "proposed_use": "residential",
            "test_lot_sqft": 5000  # PID-101 has 5000, but low transit score
        }
    }
    
    tc = test_cases.get(args.test_case, test_cases["TC-1"])
    result = simulator.run_test_case(
        tc["name"],
        tc["allowable_use"],
        tc.get("min_lot_sqft"),
        tc.get("proposed_use"),
        tc.get("test_lot_sqft")
    )
    
    simulator.print_metrics()
    
    # Save metrics to JSON file for dashboard
    import json
    metrics_file = Path("metrics.json")
    metrics_output = {
        "test_case": args.test_case,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "latencies": simulator.metrics["latencies"],
        "a2a_deliveries": simulator.metrics["a2a_deliveries"],
        "errors": simulator.metrics["errors"],
        "start_time": simulator.metrics["start_time"],
        "end_time": simulator.metrics["end_time"]
    }
    with open(metrics_file, "w") as f:
        json.dump(metrics_output, f, indent=2)
    
    if result:
        print("\n[SUCCESS] Test case completed successfully")
        sys.exit(0)
    else:
        print("\n[FAIL] Test case failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
