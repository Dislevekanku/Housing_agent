"""
Trust and Provenance Logging Module

Uses shared trust ledger for multi-agent provenance tracking.
"""
import sys
from pathlib import Path

# Import shared ledger (adjust path as needed)
_shared_ledger_path = Path(__file__).parent.parent / "shared_trust_ledger.py"
if _shared_ledger_path.exists():
    sys.path.insert(0, str(_shared_ledger_path.parent))
    from shared_trust_ledger import shared_ledger as trust_logger
else:
    # Fallback to local logger if shared not found
    import json
    import hashlib
    from datetime import datetime, timezone
    from typing import Dict, Any, Optional
    
    class TrustLogger:
        def __init__(self, log_dir: str = "logs"):
            from pathlib import Path
            self.log_dir = Path(log_dir)
            self.log_dir.mkdir(exist_ok=True)
            self.log_file = self.log_dir / "provenance.jsonl"
        
        def log_action(self, agent: str, action: str, input_ref: Optional[str] = None,
                      output: Optional[Dict[str, Any]] = None, facts_id: Optional[str] = None,
                      parent_facts_id: Optional[str] = None) -> Dict[str, Any]:
            timestamp = datetime.now(timezone.utc).isoformat()
            if not facts_id:
                seed = f"{agent}_{action}_{timestamp}"
                facts_id = f"af_{hashlib.sha256(seed.encode()).hexdigest()[:8]}"
            output_str = json.dumps(output or {}, sort_keys=True)
            sig = hashlib.sha256(output_str.encode()).hexdigest()[:16]
            output_hash = f"sha256:{hashlib.sha256(output_str.encode()).hexdigest()}" if output else None
            log_entry = {
                "ts": timestamp, "agent": agent, "action": action,
                "input_ref": input_ref, "output_facts_id": facts_id,
                "sig": sig, "hash": output_hash, "parent_facts_id": parent_facts_id
            }
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
            return {"signed_by": agent, "sig": sig, "facts_id": facts_id}
    
    trust_logger = TrustLogger()
