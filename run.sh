#!/bin/bash
echo "=========================================="
echo "   Phone Mouse & Keyboard Controller"
echo "=========================================="
echo ""
echo "Starting server..."
echo "Make sure your phone is on the same WiFi!"
echo ""
echo "The server URL will appear below:"
echo "Copy this URL and open it on your phone"
echo ""
echo "=========================================="
python3 minimal_server.py
echo ""
echo "Server stopped. Press any key to exit..."
read -n 1