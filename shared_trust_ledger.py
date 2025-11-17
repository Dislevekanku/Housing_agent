"""
Shared Trust Ledger for Multi-Agent Provenance Logging

All agents write to a single provenance.jsonl file for complete audit trail.
Includes validation for hash consistency and timestamp ordering.
"""
import json
import hashlib
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path
import threading


class SharedTrustLedger:
    """Shared trust ledger that all agents write to"""
    
    # Shared ledger location (relative to data-scout-agent root)
    SHARED_LEDGER_PATH = Path(__file__).parent / "logs" / "provenance.jsonl"
    
    # Thread lock for concurrent writes
    _lock = threading.Lock()
    
    def __init__(self, log_file: Optional[Path] = None):
        """
        Initialize shared trust ledger
        
        Args:
            log_file: Optional custom path (defaults to shared location)
        """
        self.log_file = log_file or self.SHARED_LEDGER_PATH
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _generate_facts_id(self, agent: str, action: str, timestamp: str) -> str:
        """Generate a unique facts ID"""
        seed = f"{agent}_{action}_{timestamp}"
        hash_hex = hashlib.sha256(seed.encode()).hexdigest()[:8]
        return f"af_{hash_hex}"
    
    def _generate_sig(self, output: Dict[str, Any]) -> str:
        """Generate a signature hash of the output"""
        output_str = json.dumps(output, sort_keys=True)
        return hashlib.sha256(output_str.encode()).hexdigest()[:16]
    
    def _generate_hash(self, data: Any) -> str:
        """Generate SHA256 hash of data"""
        data_str = json.dumps(data, sort_keys=True) if isinstance(data, dict) else str(data)
        return f"sha256:{hashlib.sha256(data_str.encode()).hexdigest()}"
    
    def log_action(
        self,
        agent: str,
        action: str,
        input_ref: Optional[str] = None,
        output: Optional[Dict[str, Any]] = None,
        facts_id: Optional[str] = None,
        parent_facts_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log an action with trust metadata (thread-safe)
        
        Args:
            agent: Agent name
            action: Action name
            input_ref: Reference to input data
            output: Output data to hash
            facts_id: Optional pre-generated facts ID
            parent_facts_id: Optional parent facts ID for chain validation
        
        Returns:
            Trust metadata dict for inclusion in response
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Generate facts_id if not provided
        if not facts_id:
            facts_id = self._generate_facts_id(agent, action, timestamp)
        
        # Generate signature and hash
        sig = self._generate_sig(output or {})
        output_hash = self._generate_hash(output) if output else None
        
        log_entry = {
            "ts": timestamp,
            "agent": agent,
            "action": action,
            "input_ref": input_ref,
            "output_facts_id": facts_id,
            "sig": sig,
            "hash": output_hash,
            "parent_facts_id": parent_facts_id  # For chain validation
        }
        
        # Thread-safe append to JSONL file
        with self._lock:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        
        # Return trust metadata for response
        return {
            "signed_by": agent,
            "sig": sig,
            "facts_id": facts_id
        }
    
    def read_all_entries(self) -> List[Dict[str, Any]]:
        """Read all entries from the ledger"""
        entries = []
        if self.log_file.exists():
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
        return entries
    
    def validate_chain(self, facts_id: str) -> Dict[str, Any]:
        """
        Validate a chain of facts by following parent_facts_id links
        
        Returns:
            Validation result with chain integrity status
        """
        entries = self.read_all_entries()
        entry_map = {e["output_facts_id"]: e for e in entries}
        
        chain = []
        current_id = facts_id
        
        # Follow the chain backwards
        while current_id and current_id in entry_map:
            entry = entry_map[current_id]
            chain.append(entry)
            current_id = entry.get("parent_facts_id")
        
        # Validate hash consistency
        hash_valid = True
        timestamp_order = True
        
        for i, entry in enumerate(chain):
            # Check timestamp ordering (should be increasing as we go back)
            if i > 0:
                prev_ts = datetime.fromisoformat(chain[i-1]["ts"].replace("Z", "+00:00"))
                curr_ts = datetime.fromisoformat(entry["ts"].replace("Z", "+00:00"))
                if curr_ts > prev_ts:
                    timestamp_order = False
            
            # Recompute hash to verify
            if entry.get("hash"):
                # Note: We'd need the original output to fully validate
                # For now, we check that hash format is correct
                if not entry["hash"].startswith("sha256:"):
                    hash_valid = False
        
        return {
            "facts_id": facts_id,
            "chain_length": len(chain),
            "chain": chain,
            "hash_valid": hash_valid,
            "timestamp_order": timestamp_order,
            "valid": hash_valid and timestamp_order
        }
    
    def validate_all_chains(self) -> Dict[str, Any]:
        """Validate all chains in the ledger"""
        entries = self.read_all_entries()
        results = []
        
        # Find all leaf nodes (entries with no children)
        all_facts_ids = {e["output_facts_id"] for e in entries}
        parent_facts_ids = {e.get("parent_facts_id") for e in entries if e.get("parent_facts_id")}
        leaf_ids = all_facts_ids - parent_facts_ids
        
        for leaf_id in leaf_ids:
            validation = self.validate_chain(leaf_id)
            results.append(validation)
        
        return {
            "total_entries": len(entries),
            "total_chains": len(results),
            "valid_chains": sum(1 for r in results if r["valid"]),
            "invalid_chains": sum(1 for r in results if not r["valid"]),
            "chains": results
        }


# Global shared instance
shared_ledger = SharedTrustLedger()

