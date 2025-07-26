#!/bin/bash

# One-Command Attack Simulation Starter

echo "Starting Password Attack Simulations..."

# Cleanup any existing processes on ports 8080 and 8081
echo "Checking for existing processes on ports 8080 and 8081..."
for port in 8080 8081; do
    pid=$(lsof -ti :$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "Killing existing process on port $port (PID: $pid)"
        kill $pid 2>/dev/null
        sleep 1
    fi
done

# Setup Docker
echo "123456" | sudo -S systemctl start docker > /dev/null 2>&1
echo "123456" | sudo -S chmod 666 /var/run/docker.sock > /dev/null 2>&1

# Dictionary Attack - Terminal 1
gnome-terminal --title="Dictionary Attack Server (Port 8080)" -- bash -c "
    cd dictionary_attack/victim
    echo '=== Dictionary Attack Victim Server ==='
    echo 'Starting authentication server on port 8080...'
    echo 'Default credentials: admin:secret, user:password123, test:test123, root:toor, guest:guest'
    echo ''
    python3 auth_server.py --docker
    echo ''
    echo '=== Server stopped ==='
    echo 'Press Enter to close terminal...'
    read
" &

sleep 2

# Dictionary Attack - Terminal 2  
gnome-terminal --title="Dictionary Attacker" -- bash -c "
    cd dictionary_attack/attacker
    echo '=== Dictionary Attack Client ==='
    echo 'Starting packet-level dictionary attack simulation...'
    echo 'Detailed TCP/IP packet logging enabled'
    echo ''
    echo 'Running: python3 dictionary_attacker.py --host 127.0.0.1 --port 8080 --username admin --src-ip 192.168.1.100 --wordlist wordlist.txt'
    echo ''
    python3 dictionary_attacker.py --host 127.0.0.1 --port 8080 --username admin --src-ip 192.168.1.100 --wordlist wordlist.txt
    echo ''
    echo '=== Attack completed ==='
    echo 'Press Enter to close terminal...'
    read
" &

sleep 2

# Known Password Attack - Terminal 3
gnome-terminal --title="Known Password Server (Port 8081)" -- bash -c "
    cd known_password_attack/victim
    echo '=== Known Password Attack Victim Server ==='
    echo 'Starting user profile server on port 8081...'
    echo 'OSINT-based target profiles:'
    echo '  john.smith:John1985! (FirstName + BirthYear + Special)'
    echo '  sarah.jones:Luna2024 (PetName + CurrentYear)'
    echo '  mike.johnson:Chicago78! (Hometown + BirthYear + Special)'
    echo '  anna.wilson:Bella@90 (PetName + BirthYear + Special)'
    echo '  david.brown:Dolphins83 (FavoriteTeam + BirthYear)'
    echo ''
    python3 auth_server.py --docker
    echo ''
    echo '=== Server stopped ==='
    echo 'Press Enter to close terminal...'
    read
" &

sleep 2

# Known Password Attack - Terminal 4
gnome-terminal --title="Known Password Attacker" -- bash -c "
    cd known_password_attack/attacker
    echo '=== Known Password Attack Client ==='
    echo 'Starting OSINT-based packet-level attack...'
    echo 'Detailed TCP/IP packet logging enabled'
    echo ''
    echo 'Running: python3 known_password_attacker.py --host 127.0.0.1 --port 8081 --username john.smith --src-ip 192.168.1.101 --max-attempts 15'
    echo ''
    python3 known_password_attacker.py --host 127.0.0.1 --port 8081 --username john.smith --src-ip 192.168.1.101 --max-attempts 15
    echo ''
    echo '=== Attack completed ==='
    echo 'Press Enter to close terminal...'
    read
" &

echo ""
echo "✅ All attack simulations started!"
echo ""
echo "📋 Running Simulations:"
echo "   🎯 Dictionary Attack: Victim (Port 8080) + Packet-Level Attacker"
echo "   🎯 Known Password Attack: Victim (Port 8081) + OSINT Packet-Level Attacker"
echo ""
echo "📱 4 terminal windows opened for interactive simulation"
echo "⚠️  Both attackers show detailed TCP/IP packet analysis"
echo "⚠️  Known password attacker uses OSINT-based password generation"
echo ""
echo "🛑 To stop: Close terminal windows or press Ctrl+C in each"