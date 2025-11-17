#!/usr/bin/env python3
"""
Extract metrics from simulation and trust ledger for dashboard
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from shared_trust_ledger import SharedTrustLedger
from collections import defaultdict


def extract_metrics():
    """Extract all metrics from trust ledger and simulation artifacts"""
    ledger = SharedTrustLedger()
    entries = ledger.read_all_entries()
    
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "total_entries": len(entries),
        "by_agent": defaultdict(int),
        "by_action": defaultdict(int),
        "chains": {},
        "latencies": {},
        "interactions": [],
        "coverage": {}
    }
    
    # Count by agent and action
    for entry in entries:
        metrics["by_agent"][entry["agent"]] += 1
        metrics["by_action"][entry["action"]] += 1
    
    # Extract chains
    validation_result = ledger.validate_all_chains()
    metrics["chains"] = {
        "total": validation_result["total_chains"],
        "valid": validation_result["valid_chains"],
        "invalid": validation_result["invalid_chains"]
    }
    
    # Extract latencies from artifacts if available
    artifacts_dir = Path("artifacts")
    if artifacts_dir.exists():
        for parcel_dir in artifacts_dir.iterdir():
            if parcel_dir.is_dir():
                packet_file = parcel_dir / "packet.json"
                if packet_file.exists():
                    with open(packet_file) as f:
                        packet = json.load(f)
                        if "trust" in packet:
                            facts_id = packet["trust"]["facts_id"]
                            # Try to find latency info in simulation logs
                            # For now, we'll use placeholder
                            pass
    
    # Extract interactions (A2A messages)
    a2a_entries = [e for e in entries if e["action"] == "a2a_receive"]
    metrics["interactions"] = [
        {
            "agent": e["agent"],
            "timestamp": e["ts"],
            "msg_id": e.get("input_ref", "").replace("msg_id:", "")
        }
        for e in a2a_entries
    ]
    
    # Calculate coverage (percentage of entries with parent links)
    entries_with_parent = sum(1 for e in entries if e.get("parent_facts_id"))
    metrics["coverage"] = {
        "entries_with_parent": entries_with_parent,
        "total_entries": len(entries),
        "coverage_percentage": (entries_with_parent / len(entries) * 100) if entries else 0
    }
    
    # Convert defaultdicts to regular dicts for JSON serialization
    metrics["by_agent"] = dict(metrics["by_agent"])
    metrics["by_action"] = dict(metrics["by_action"])
    
    return metrics


def load_simulation_metrics():
    """Load metrics from simulate_flow.py if available"""
    # This would require parsing simulation output or storing metrics
    # For now, return empty dict
    return {}


if __name__ == "__main__":
    metrics = extract_metrics()
    
    # Merge with simulation metrics if available
    sim_metrics = load_simulation_metrics()
    if sim_metrics.get("latencies"):
        metrics["latencies"].update(sim_metrics["latencies"])
    
    # Write to JSON file for dashboard
    output_file = Path("metrics.json")
    with open(output_file, "w") as f:
        json.dump(metrics, f, indent=2)
    
    print(f"Metrics extracted and saved to {output_file}")
    print(f"Total entries: {metrics['total_entries']}")
    print(f"Valid chains: {metrics['chains']['valid']}/{metrics['chains']['total']}")
    print(f"Coverage: {metrics['coverage']['coverage_percentage']:.1f}%")

