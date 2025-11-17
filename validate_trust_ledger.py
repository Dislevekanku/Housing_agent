#!/usr/bin/env python3
"""
Trust Ledger Validation Tool

Validates hash consistency and timestamp ordering across all agents.
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from shared_trust_ledger import SharedTrustLedger


def validate_ledger():
    """Validate the shared trust ledger"""
    ledger = SharedTrustLedger()
    
    print("=" * 60)
    print("Trust Ledger Validation")
    print("=" * 60)
    
    # Read all entries
    entries = ledger.read_all_entries()
    print(f"\nTotal entries: {len(entries)}")
    
    if not entries:
        print("No entries found in ledger")
        return
    
    # Group by agent
    by_agent = {}
    for entry in entries:
        agent = entry["agent"]
        if agent not in by_agent:
            by_agent[agent] = []
        by_agent[agent].append(entry)
    
    print(f"\nEntries by agent:")
    for agent, agent_entries in by_agent.items():
        print(f"  {agent}: {len(agent_entries)}")
    
    # Validate all chains
    print("\n" + "=" * 60)
    print("Chain Validation")
    print("=" * 60)
    
    validation_result = ledger.validate_all_chains()
    
    print(f"\nTotal chains: {validation_result['total_chains']}")
    print(f"Valid chains: {validation_result['valid_chains']}")
    print(f"Invalid chains: {validation_result['invalid_chains']}")
    
    # Show chain details
    print("\nChain Details:")
    for chain_result in validation_result["chains"]:
        facts_id = chain_result["facts_id"]
        chain_length = chain_result["chain_length"]
        valid = chain_result["valid"]
        status = "[OK]" if valid else "[FAIL]"
        
        print(f"\n{status} Chain: {facts_id}")
        print(f"  Length: {chain_length}")
        print(f"  Hash valid: {chain_result['hash_valid']}")
        print(f"  Timestamp order: {chain_result['timestamp_order']}")
        
        if chain_result["chain"]:
            print("  Chain:")
            for i, entry in enumerate(chain_result["chain"]):
                print(f"    {i+1}. {entry['agent']} - {entry['action']} ({entry['ts']})")
                if entry.get("parent_facts_id"):
                    print(f"       Parent: {entry['parent_facts_id']}")
    
    # Check timestamp ordering across all entries
    print("\n" + "=" * 60)
    print("Timestamp Ordering Check")
    print("=" * 60)
    
    timestamps = []
    for entry in entries:
        ts_str = entry["ts"]
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            timestamps.append((ts, entry))
        except Exception as e:
            print(f"Warning: Invalid timestamp in entry: {e}")
    
    timestamps.sort(key=lambda x: x[0])
    
    print(f"\nEntries in chronological order:")
    for ts, entry in timestamps[:10]:  # Show first 10
        print(f"  {ts.isoformat()} - {entry['agent']} - {entry['action']}")
    
    if len(timestamps) > 10:
        print(f"  ... and {len(timestamps) - 10} more")
    
    # Check for hash consistency
    print("\n" + "=" * 60)
    print("Hash Format Validation")
    print("=" * 60)
    
    hash_issues = []
    for entry in entries:
        hash_val = entry.get("hash")
        if hash_val and not hash_val.startswith("sha256:"):
            hash_issues.append(entry)
        elif not hash_val:
            hash_issues.append(entry)
    
    if hash_issues:
        print(f"\n[WARNING] Found {len(hash_issues)} entries with hash issues:")
        for entry in hash_issues[:5]:
            print(f"  {entry['agent']} - {entry['action']} - hash: {entry.get('hash', 'MISSING')}")
    else:
        print("\n[OK] All entries have valid hash format")
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_valid = (
        validation_result['invalid_chains'] == 0 and
        len(hash_issues) == 0
    )
    
    if all_valid:
        print("\n[SUCCESS] All chains are valid!")
        return 0
    else:
        print("\n[FAIL] Some validation issues found")
        return 1


if __name__ == "__main__":
    sys.exit(validate_ledger())

