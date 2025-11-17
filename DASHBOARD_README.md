# Trust Ledger Dashboard

A lightweight web-based dashboard for visualizing trust signatures, agent interactions, and performance metrics.

## Quick Start

### Option 1: Simple HTTP Server (Recommended)

```bash
python serve_dashboard.py
```

This will:
- Start a local server on `http://localhost:8080`
- Automatically open the dashboard in your browser
- Serve all required files (dashboard.html, logs/provenance.jsonl, metrics.json)

### Option 2: Direct File Access

Simply open `dashboard.html` in your web browser. Note: Some browsers may block local file access for security reasons.

### Option 3: Python HTTP Server

```bash
# Python 3
python -m http.server 8080

# Then navigate to http://localhost:8080/dashboard.html
```

## Features

### 1. Real-time Metrics
- Total ledger entries
- Valid chains count
- Agent interactions
- Average latency

### 2. Chain Visualization
- Visual representation of complete chains
- Parent-child relationships
- Timestamp ordering
- Hash verification

### 3. Trust Signatures
- Grid view of all signatures
- Agent badges
- Facts IDs
- Timestamps
- Validation status

### 4. Agent Interactions
- Flow diagram showing agent communication
- Action counts per agent
- Visual flow representation

### 5. Latency Metrics
- Bar charts showing performance
- Operation-by-operation breakdown
- Relative performance visualization

## Data Sources

The dashboard reads from:
- `logs/provenance.jsonl` - Trust ledger entries
- `metrics.json` - Performance metrics (optional)

## Auto-refresh

The dashboard automatically refreshes every 5 seconds to show the latest data.

## Troubleshooting

### "Error loading data"
- Make sure the agents have been run at least once
- Verify `logs/provenance.jsonl` exists
- Check browser console for detailed error messages

### "No latency data available"
- Run the simulation: `python simulate_flow.py --test-case TC-1`
- This will generate `metrics.json` with latency data

### CORS Errors
- Use the provided `serve_dashboard.py` script
- Or serve via HTTP server (not file://)

## Customization

The dashboard is a single HTML file with embedded CSS and JavaScript. You can:
- Modify colors in the `<style>` section
- Adjust refresh interval (currently 5000ms)
- Add new visualizations in the JavaScript section

## Browser Compatibility

Tested on:
- Chrome/Edge (Chromium)
- Firefox
- Safari

Requires modern browser with:
- Fetch API support
- ES6 JavaScript
- CSS Grid support

