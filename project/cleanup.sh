#!/bin/bash

# Cleanup script for password attack simulations

echo "Cleaning up password attack simulation processes..."

# Kill processes using ports 8080 and 8081
for port in 8080 8081; do
    pid=$(lsof -ti :$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "Killing process on port $port (PID: $pid)"
        kill $pid 2>/dev/null
        sleep 1
        
        # Force kill if still running
        if kill -0 $pid 2>/dev/null; then
            echo "Force killing process on port $port"
            kill -9 $pid 2>/dev/null
        fi
    else
        echo "Port $port is free"
    fi
done

# Kill any remaining Python processes related to our attack simulation
pkill -f "dictionary_attacker.py" 2>/dev/null
pkill -f "known_password_attacker.py" 2>/dev/null
pkill -f "auth_server.py" 2>/dev/null

echo "Cleanup completed!"
echo "You can now run ./start.sh to start fresh simulations."