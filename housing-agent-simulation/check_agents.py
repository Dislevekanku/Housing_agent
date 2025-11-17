#!/usr/bin/env python3
"""
Check if all agents are running and healthy
"""
import requests
import sys

AGENTS = {
    "Data Scout": "http://localhost:8000",
    "Compliance": "http://localhost:8001",
    "Permit Liaison": "http://localhost:8002"
}

def check_agent(name: str, url: str) -> bool:
    """Check if an agent is healthy"""
    try:
        response = requests.get(f"{url}/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] {name}: {data.get('status', 'unknown')} (v{data.get('version', '?')})")
            return True
        else:
            print(f"[FAIL] {name}: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"[FAIL] {name}: Connection refused (not running?)")
        return False
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        return False

def main():
    print("Checking agents...\n")
    all_ok = True
    
    for name, url in AGENTS.items():
        if not check_agent(name, url):
            all_ok = False
    
    print()
    if all_ok:
        print("[SUCCESS] All agents are healthy!")
        sys.exit(0)
    else:
        print("[ERROR] Some agents are not running")
        print("\nTo start agents, run:")
        print("  Windows: run_agents.bat")
        print("  Linux/Mac: ./run_agents.sh")
        sys.exit(1)

if __name__ == "__main__":
    main()
