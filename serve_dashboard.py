#!/usr/bin/env python3
"""
Simple HTTP server to serve the trust ledger dashboard
"""
import http.server
import socketserver
import webbrowser
from pathlib import Path
import os
import socket

DEFAULT_PORT = 8080
DIRECTORY = Path(__file__).parent


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()


def is_port_available(port):
    """Check if a port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('', port))
            return True
        except OSError:
            return False


def find_available_port(start_port=DEFAULT_PORT, max_attempts=10):
    """Find an available port starting from start_port"""
    for i in range(max_attempts):
        port = start_port + i
        if is_port_available(port):
            return port
    return None


def main():
    os.chdir(DIRECTORY)
    
    # Try to find an available port
    port = find_available_port()
    if port is None:
        print("Error: Could not find an available port. Please close other servers or try a different port range.")
        return
    
    if port != DEFAULT_PORT:
        print(f"Port {DEFAULT_PORT} is in use, using port {port} instead")
    
    try:
        with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as httpd:
            url = f"http://localhost:{port}/dashboard.html"
            print(f"=" * 60)
            print(f"Dashboard server started at {url}")
            print(f"Press Ctrl+C to stop the server")
            print(f"=" * 60)
            
            # Try to open browser automatically
            try:
                webbrowser.open(url)
                print(f"Opening dashboard in browser...")
            except Exception as e:
                print(f"Could not open browser automatically: {e}")
                print(f"Please manually navigate to: {url}")
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nServer stopped")
    except OSError as e:
        print(f"Error starting server: {e}")
        print(f"Port {port} may have been taken. Try closing other applications using this port.")


if __name__ == "__main__":
    main()

