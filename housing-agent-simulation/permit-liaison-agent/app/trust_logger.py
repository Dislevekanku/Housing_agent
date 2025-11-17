"""
Trust and Provenance Logging Module

Appends structured logs to provenance.jsonl for audit trail and trust tracking.
"""
import json
import hashlib
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path


class TrustLogger:
    """Logs trust/provenance events to JSONL file"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / "provenance.jsonl"
    
    def _generate_facts_id(self, agent: str, action: str) -> str:
        """Generate a unique facts ID (simplified: af_<timestamp>_<hash>"""
        timestamp = datetime.now(timezone.utc).isoformat()
        seed = f"{agent}_{action}_{timestamp}"
        hash_hex = hashlib.sha256(seed.encode()).hexdigest()[:8]
        return f"af_{hash_hex}"
    
    def _generate_sig(self, output: Dict[str, Any]) -> str:
        """Generate a simple signature hash of the output"""
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
        facts_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log an action with trust metadata
        
        Returns the trust metadata dict for inclusion in response
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Generate facts_id if not provided
        if not facts_id:
            facts_id = self._generate_facts_id(agent, action)
        
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
            "hash": output_hash
        }
        
        # Append to JSONL file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        # Return trust metadata for response
        return {
            "signed_by": agent,
            "sig": sig,
            "facts_id": facts_id
        }


# Global instance
trust_logger = TrustLogger()
