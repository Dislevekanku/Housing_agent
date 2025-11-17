# Trust Ledger Summary

## Overview
The shared trust ledger (`logs/provenance.jsonl`) provides a complete audit trail for all agent actions across the zoning → compliance → permit packet flow.

## Latest Chain (TC-1 Test Case)

### Complete Chain: `af_65784a31`

```
1. data-scout - find_candidates
   Timestamp: 2025-11-17T01:55:28.015288+00:00
   Facts ID: af_8d5e5ab3
   Input: query:residential
   Hash: sha256:75b5993cb50c34dd76d203b1b546d81cd18ace953bc7c1f087c50dbcaf1b026f
   Parent: None (root of chain)

2. compliance - check_compliance
   Timestamp: 2025-11-17T01:55:32.263248+00:00
   Facts ID: af_9e3e7e99
   Input: parcel:PID-103
   Hash: sha256:c81e3f7fc63c942471187e6940cae08621153430c31c80a11440394b664a071a
   Parent: af_8d5e5ab3 (links to Data Scout)

3. permit-liaison - prepare_packet
   Timestamp: 2025-11-17T01:55:36.427794+00:00
   Facts ID: af_65784a31
   Input: parcel:PID-103
   Hash: sha256:11ec78fc7b86d2c88aab288a1d98aa9e38e4dd3d6b0d1964d1758e3e63909641
   Parent: af_9e3e7e99 (links to Compliance)
```

## Validation Results

✅ **All chains valid**: 20/20 chains passed validation
✅ **Hash consistency**: All entries have valid SHA256 hash format
✅ **Timestamp ordering**: All timestamps are in correct chronological order
✅ **Parent-child links**: All parent_facts_id references are valid

## Statistics

- **Total entries**: 22
- **By agent**:
  - data-scout: 17 entries
  - compliance: 3 entries
  - permit-liaison: 2 entries

## Chain Validation Features

1. **Hash Verification**: Each entry includes a SHA256 hash of the output data
2. **Timestamp Ordering**: Validates that parent entries occur before child entries
3. **Parent-Child Links**: Tracks the provenance chain through `parent_facts_id`
4. **Thread-Safe Writes**: All agents write to the same ledger safely

## Usage

### View the ledger
```bash
cat logs/provenance.jsonl
```

### Validate all chains
```bash
python validate_trust_ledger.py
```

### Validate a specific chain
```python
from shared_trust_ledger import shared_ledger
result = shared_ledger.validate_chain("af_65784a31")
print(result)
```

## Trust Metadata Structure

Each entry contains:
- `ts`: ISO 8601 timestamp (UTC)
- `agent`: Agent name
- `action`: Action performed
- `input_ref`: Reference to input data
- `output_facts_id`: Unique identifier for this output
- `sig`: Signature hash (16 chars)
- `hash`: Full SHA256 hash of output
- `parent_facts_id`: Link to parent entry (if part of a chain)

