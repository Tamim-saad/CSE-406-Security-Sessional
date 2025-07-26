#!/bin/bash

# One-Command Attack Simulation Starter

echo "Starting Password Attack Simulations..."

# Setup Docker
echo "123456" | sudo -S systemctl start docker > /dev/null 2>&1
echo "123456" | sudo -S chmod 666 /var/run/docker.sock > /dev/null 2>&1

# Dictionary Attack - Terminal 1
gnome-terminal --title="Dictionary Attack Server (Port 8080)" -- bash -c "
    cd dictionary_attack/victim
    echo '=== Dictionary Attack Victim Server ==='
    echo 'Starting authentication server on port 8080...'
    python3 auth_server.py --docker
" &

sleep 2

# Dictionary Attack - Terminal 2  
gnome-terminal --title="Dictionary Attacker" -- bash -c "
    cd dictionary_attack/attacker
    echo '=== Dictionary Attack Client ==='
    echo 'Starting dictionary attack...'
    python3 dictionary_attacker.py
" &

sleep 2

# Known Password Attack - Terminal 3
gnome-terminal --title="Known Password Server (Port 8081)" -- bash -c "
    cd known_password_attack/victim
    echo '=== Known Password Attack Victim Server ==='
    echo 'Starting user profile server on port 8081...'
    python3 auth_server.py --docker
" &

sleep 2

# Known Password Attack - Terminal 4
gnome-terminal --title="Known Password Attacker" -- bash -c "
    cd known_password_attack/attacker
    echo '=== Known Password Attack Client ==='
    echo 'Starting OSINT-based attack...'
    python3 known_password_attacker.py
" &

echo ""
echo "✅ All attack simulations started!"
echo ""
echo "📋 Running Simulations:"
echo "   🎯 Dictionary Attack: Victim (Port 8080) + Attacker"
echo "   🎯 Known Password Attack: Victim (Port 8081) + Attacker"
echo ""
echo "📱 4 terminal windows opened for interactive simulation"
echo ""
echo "🛑 To stop: Close terminal windows or press Ctrl+C in each"