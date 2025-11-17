# Zoning → Permit Data Flow Simulation - Implementation Summary

## Overview

This simulation implements a complete end-to-end flow from parcel discovery → zoning/compliance check → permit-readiness packet generation using three microservice agents with MCP tools and A2A messaging.

## Architecture

### Agents

1. **Data Scout Agent** (Port 8000)
   - MCP Tool: `find_candidates`
   - Finds candidate parcels based on zoning and lot size
   - Endpoints: `/health`, `/mcp/tools`, `/mcp/invoke/find_candidates`, `/a2a`

2. **Compliance Agent** (Port 8001)
   - MCP Tool: `check_compliance`
   - Evaluates zoning and code compliance
   - Endpoints: `/health`, `/mcp/tools`, `/mcp/invoke/check_compliance`, `/a2a`

3. **Permit Liaison Agent** (Port 8002)
   - MCP Tool: `prepare_packet`
   - Assembles permit-readiness packets
   - Endpoints: `/health`, `/mcp/tools`, `/mcp/invoke/prepare_packet`, `/a2a`

### Data Flow

```
1. Data Scout finds candidates
   ↓ (A2A message)
2. Compliance checks zoning/code
   ↓ (A2A message)
3. Permit Liaison assembles packet
   ↓ (A2A ack messages)
4. Data Scout + Compliance receive completion
```

### Trust/Provenance Logging

All agents log actions to `logs/provenance.jsonl` with:
- Timestamp
- Agent name
- Action type
- Input reference
- Output facts ID
- Signature hash
- Output hash

## File Structure

```
housing_agent/data-scout-agent/
├── fixtures/
│   ├── parcels.csv          # Mock parcel data
│   ├── zoning_rules.json    # Zoning regulations
│   └── code_policies.json   # Building code policies
├── app/                     # Data Scout Agent
│   ├── main.py
│   ├── models.py
│   ├── mcp_tools.py
│   ├── trust_logger.py
│   └── services/
├── compliance-agent/        # Compliance Agent
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── compliance_checker.py
│   │   └── trust_logger.py
│   └── requirements.txt
├── permit-liaison-agent/     # Permit Liaison Agent
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── packet_builder.py
│   │   └── trust_logger.py
│   └── requirements.txt
├── simulate_flow.py          # Main simulation runner
├── test_simulation.py        # Test runner
├── check_agents.py          # Agent health checker
├── run_agents.bat           # Windows startup script
├── run_agents.sh            # Linux/Mac startup script
├── README_SIMULATION.md     # User guide
├── RESULTS.md               # Results template
└── requirements.txt
```

## Test Cases

- **TC-1**: Happy Path (R-3 residential, lot 7000 sqft) - Should pass
- **TC-2**: Fails Min Lot (MR-1 residential, lot 4000 sqft) - Should fail
- **TC-3**: Mixed-use in CC-2 (lot 12000 sqft) - Should pass with flags
- **TC-4**: Low score candidate - May be filtered out

## Usage

### Start Agents

```bash
# Windows
run_agents.bat

# Linux/Mac
chmod +x run_agents.sh
./run_agents.sh
```

### Check Agent Health

```bash
python check_agents.py
```

### Run Simulation

```bash
# Single test case
python simulate_flow.py --test-case TC-1

# All test cases
python test_simulation.py
```

## Outputs

- **Artifacts**: `artifacts/{parcel_id}/packet.json`
- **Logs**: `logs/provenance.jsonl`
- **Test Results**: `artifacts/test_results.json`

## Next Steps

1. **Real Data Integration**
   - Connect to Boston Assessor parcels
   - Integrate real zoning ordinance database
   - Connect to ISD permit API

2. **Verifiable Credentials**
   - Add JWT/JSON-LD credentials
   - Implement AgentFacts integration
   - Register with NEST

3. **Enhanced Features**
   - PDF packet generation (WeasyPrint)
   - Docker-compose for all agents
   - Trust ledger dashboard

4. **Production Deployment**
   - Deploy to EC2/NEST
   - Add monitoring/alerting
   - Implement A2A retry logic

## Metrics Captured

- Latency per agent operation
- End-to-end flow time
- A2A delivery success rate
- Determinism (same input → same output hash)
- Trust coverage (% of steps with signed outputs)

## Notes

- A2A messaging uses HTTP POST with envelope format
- Trust logging uses simplified signature hashing (production should use proper crypto)
- Mock data in `fixtures/` for local testing
- All agents use FastAPI with CORS enabled for development
