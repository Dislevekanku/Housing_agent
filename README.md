# Housing Agent Simulation: Zoning → Permit Data Flow

A complete end-to-end simulation demonstrating agent coordination for housing development permits, from parcel discovery through compliance checking to permit packet generation.

## Overview

This project simulates a multi-agent system for processing housing development permits:

1. **Data Scout Agent** - Discovers candidate parcels based on zoning and lot size
2. **Compliance Agent** - Evaluates zoning and building code compliance
3. **Permit Liaison Agent** - Assembles permit-readiness packets with routing and timelines

The system demonstrates:
- **MCP (Model Context Protocol)** tools for agent capabilities
- **A2A (Agent-to-Agent)** messaging between services
- **Trust/Provenance Logging** for audit trails and verifiability

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────────┐
│  Data Scout     │ A2A  │   Compliance     │ A2A  │  Permit Liaison    │
│     Agent       │─────>│     Agent        │─────>│      Agent          │
│  (Port 8000)    │      │   (Port 8001)    │      │    (Port 8002)      │
└─────────────────┘      └──────────────────┘      └─────────────────────┘
       │                          │                          │
       │                          │                          │
       └──────────────────────────┴──────────────────────────┘
                           Trust/Provenance Logging
```

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

1. **Install dependencies for all agents:**

```bash
# Data Scout Agent
pip install -r requirements.txt

# Compliance Agent
cd compliance-agent
pip install -r requirements.txt
cd ..

# Permit Liaison Agent
cd permit-liaison-agent
pip install -r requirements.txt
cd ..
```

### Running the Simulation

1. **Start all agents:**

```bash
# Windows
run_agents.bat

# Linux/Mac
chmod +x run_agents.sh
./run_agents.sh
```

This will start three agents in separate windows/terminals:
- Data Scout Agent: http://localhost:8000
- Compliance Agent: http://localhost:8001
- Permit Liaison Agent: http://localhost:8002

2. **Check agent health:**

```bash
python check_agents.py
```

3. **Run simulation:**

```bash
# Run a specific test case
python simulate_flow.py --test-case TC-1

# Run all test cases
python test_simulation.py
```

## Test Cases

- **TC-1**: Happy Path (R-3 residential) - Should pass and create packet
- **TC-2**: Fails Min Lot (MR-1, lot 4000) - Should fail zoning compliance
- **TC-3**: Mixed-use in CC-2 - Should pass with parking/ADA notes
- **TC-4**: Low score candidate - May be filtered or pass with notes

## Project Structure

```
housing-agent-simulation/
├── fixtures/                    # Mock data
│   ├── parcels.csv              # Sample parcel data
│   ├── zoning_rules.json        # Zoning regulations
│   └── code_policies.json       # Building code policies
├── app/                         # Data Scout Agent
│   ├── main.py                  # FastAPI application
│   ├── models.py                # Pydantic models
│   ├── mcp_tools.py             # MCP tool definitions
│   ├── trust_logger.py          # Trust/provenance logging
│   └── services/                # Business logic
│       ├── zoning_index.py      # Parcel search
│       └── scoring.py           # Candidate scoring
├── compliance-agent/            # Compliance Agent
│   ├── app/
│   │   ├── main.py
│   │   ├── compliance_checker.py
│   │   └── trust_logger.py
│   └── requirements.txt
├── permit-liaison-agent/        # Permit Liaison Agent
│   ├── app/
│   │   ├── main.py
│   │   ├── packet_builder.py
│   │   └── trust_logger.py
│   └── requirements.txt
├── simulate_flow.py             # Main simulation runner
├── test_simulation.py           # Test runner
├── check_agents.py              # Health checker
└── run_agents.bat/sh           # Startup scripts
```

## API Endpoints

Each agent provides:

- `GET /health` - Health check
- `GET /mcp/tools` - List available MCP tools
- `POST /mcp/invoke/{tool_name}` - Invoke MCP tool
- `POST /a2a` - Receive A2A messages

## A2A Message Flow

```
Data Scout → Compliance: Send candidate parcel
Compliance → Permit Liaison: Send compliance report
Permit Liaison → Data Scout + Compliance: Final packet acknowledgment
```

## Trust/Provenance Logging

All agent actions are logged to `logs/provenance.jsonl` with:
- Timestamp
- Agent name and action
- Input reference
- Output facts ID
- Signature hash
- Output hash

## Outputs

- **Artifacts**: `artifacts/{parcel_id}/packet.json` - Generated permit packets
- **Logs**: `logs/provenance.jsonl` - Trust audit trail
- **Test Results**: `artifacts/test_results.json` - Test run results

## Example Output

```json
{
  "parcel_id": "PID-103",
  "packet": {
    "checklist": [
      "Zoning determination",
      "Prelim site plan",
      "Parking study",
      "ADA accessibility plan",
      "Egress plan review"
    ],
    "attachments": ["zoning_summary.pdf", "compliance.json"],
    "routing": ["Planning", "ISD"],
    "estimated_timeline_days": 21
  },
  "trust": {
    "signed_by": "permit-liaison",
    "sig": "11ec78fc7b86d2c8",
    "facts_id": "af_6d251b03"
  }
}
```

## Metrics

The simulation captures:
- **Latency**: Per-agent operation times and end-to-end flow time
- **Reliability**: A2A delivery success rate
- **Determinism**: Same input → same output hash verification
- **Trust Coverage**: Percentage of steps with signed outputs

## Next Steps

- [ ] Integrate real Boston Assessor parcels dataset
- [ ] Connect to real zoning ordinance database
- [ ] Add Verifiable Credentials (JWT/JSON-LD)
- [ ] Implement AgentFacts integration
- [ ] Register agents with NEST
- [ ] Generate PDF packets (WeasyPrint)
- [ ] Create Docker-compose for all agents
- [ ] Build trust ledger dashboard
- [ ] Deploy to EC2/NEST

## Documentation

- `README_SIMULATION.md` - Detailed simulation guide
- `SIMULATION_SUMMARY.md` - Architecture and implementation details
- `RESULTS.md` - Test results template

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or pull request.

## Contact

For questions or issues, please open a GitHub issue.

