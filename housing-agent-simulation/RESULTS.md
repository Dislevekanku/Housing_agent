# Zoning → Permit Data Flow Simulation Results

## Overview

This document captures the results of the mock zoning → permit data-flow simulation, demonstrating end-to-end agent coordination via MCP tools and A2A messaging.

## Test Cases

### TC-1: Happy Path (R-3 residential)
- **Input**: PID-103, residential use, lot 7,000 sqft
- **Expected**: Zoning pass = true, packet created
- **Status**: ✅ PASS / ❌ FAIL

### TC-2: Fails Min Lot (residential in MR-1, lot 4,000)
- **Input**: Residential use, lot 4,000 sqft (below MR-1 min 4,500)
- **Expected**: Zoning pass = false, packet not created
- **Status**: ✅ PASS / ❌ FAIL

### TC-3: Mixed-use in CC-2
- **Input**: PID-102, mixed-use, lot 12,000 sqft
- **Expected**: Zoning pass = true, packet with parking/ADA notes
- **Status**: ✅ PASS / ❌ FAIL

### TC-4: No transit or low vacancy
- **Input**: Residential, low score candidates
- **Expected**: Candidate excluded or low score, logged
- **Status**: ✅ PASS / ❌ FAIL

## Metrics

### Latency (ms)
| Agent | Operation | Latency (ms) |
|-------|-----------|--------------|
| Data Scout | find_candidates | - |
| Compliance | check_compliance | - |
| Permit Liaison | prepare_packet | - |
| A2A | data-scout → compliance | - |
| A2A | compliance → permit-liaison | - |

### Reliability
- **A2A Delivery Success**: X/Y messages
- **Retries**: 0
- **Errors**: 0

### Determinism
- **Same Input → Same Output Hash**: ✅ Verified
- **Trust Coverage**: 100% (all steps signed)

## Trust/Provenance Logs

Sample entries from `logs/provenance.jsonl`:

```json
{
  "ts": "2025-01-28T14:06:03Z",
  "agent": "compliance",
  "action": "check_compliance",
  "input_ref": "parcel:PID-103",
  "output_facts_id": "af_0123",
  "sig": "<hex>",
  "hash": "sha256:<hash>"
}
```

## Artifacts

Generated permit packets saved to:
- `artifacts/PID-XXX/packet.json`

## Next Steps

1. **Real Data Integration**
   - Plug into Boston Assessor parcels dataset
   - Connect to real zoning ordinance database
   - Integrate with ISD permit API

2. **Verifiable Credentials (VC)**
   - Add JWT or JSON-LD credentials to compliance outputs
   - Implement AgentFacts integration
   - Register agents with NEST

3. **Enhanced Features**
   - PDF packet generation (WeasyPrint)
   - Docker-compose for all 3 agents
   - Dashboard for trust ledger visualization

4. **Production Deployment**
   - Deploy to EC2/NEST
   - Add monitoring and alerting
   - Implement retry logic for A2A messages

## Demo

See Loom video (60-90s) demonstrating the complete flow.

---

*Generated: [DATE]*
