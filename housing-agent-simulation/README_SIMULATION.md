# Zoning → Permit Data Flow Simulation

This directory contains a complete mock simulation of the zoning → permit data flow using three agents:

1. **Data Scout Agent** - Finds candidate parcels (MCP tool)
2. **Compliance Agent** - Evaluates zoning/code compliance
3. **Permit Liaison Agent** - Assembles permit-readiness packets

## Quick Start

### 1. Install Dependencies

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

### 2. Start All Agents

**Windows:**
```bash
run_agents.bat
```

**Linux/Mac:**
```bash
chmod +x run_agents.sh
./run_agents.sh
```

Or manually in separate terminals:
```bash
# Terminal 1: Data Scout (port 8000)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Compliance (port 8001)
cd compliance-agent
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 3: Permit Liaison (port 8002)
cd permit-liaison-agent
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### 3. Run Simulation

```bash
# Run a specific test case
python simulate_flow.py --test-case TC-1

# Run all test cases
python test_simulation.py
```

## Test Cases

- **TC-1**: Happy Path (R-3 residential) - Should pass and create packet
- **TC-2**: Fails Min Lot - Should fail zoning compliance
- **TC-3**: Mixed-use in CC-2 - Should pass with parking/ADA notes
- **TC-4**: Low score candidate - May be excluded

## Architecture

### Agents

Each agent provides:
- `/health` - Health check endpoint
- `/mcp/tools` - List available MCP tools
- `/mcp/invoke/{tool_name}` - Invoke MCP tool
- `/a2a` - Receive A2A messages

### A2A Message Flow

```
Data Scout → Compliance: Send candidate parcel
Compliance → Permit Liaison: Send compliance report
Permit Liaison → Data Scout + Compliance: Final packet ack
```

### Trust/Provenance Logging

All actions are logged to `logs/provenance.jsonl` with:
- Timestamp
- Agent name
- Action type
- Input reference
- Output facts ID
- Signature hash
- Output hash

## Outputs

### Artifacts

- `artifacts/{parcel_id}/packet.json` - Generated permit packets
- `artifacts/test_results.json` - Test run results

### Logs

- `logs/provenance.jsonl` - Trust/provenance audit trail

## Next Steps

See `RESULTS.md` for next steps including:
- Real Boston dataset integration
- Verifiable Credentials (VC)
- PDF packet generation
- Docker-compose deployment
- NEST registration
