# Dictionary Attack Simulation with Packet-Level Analysis

This directory contains the implementation of a Dictionary Attack simulation with detailed TCP/IP packet logging for educational and defensive security purposes.

## Overview

A Dictionary Attack is a brute-force attack method where an attacker systematically tries passwords from a predefined list (dictionary) of commonly used passwords. This implementation includes comprehensive packet-level analysis showing IP headers, TCP headers, and HTTP payload details for educational network security analysis.

## Files Structure

```
dictionary_attack/
├── attacker/
│   ├── dictionary_attacker.py    # Main attacker script
│   └── wordlist.txt              # Dictionary of passwords to try
├── victim/
│   └── auth_server.py            # Authentication server (victim system)
└── README.md                     # This file
```

## How to Run the Simulation

### Quick Start (Recommended)

From the project root directory, run:
```bash
./start.sh
```

This will automatically open 4 terminals:
1. **Dictionary Attack Victim Server** (Port 8080)
2. **Packet-Level Dictionary Attacker**
3. **Known Password Attack Victim Server** (Port 8081) 
4. **OSINT-Based Packet-Level Attacker**

### Manual Setup

#### Step 1: Start the Victim Server

Open a terminal and navigate to the victim directory:

```bash
cd dictionary_attack/victim
python3 auth_server.py --docker
```

The server will start on `0.0.0.0:8080` and display available user accounts:
- admin:secret
- user:password123
- test:test123
- root:toor
- guest:guest

#### Step 2: Run the Packet-Level Attacker

Open another terminal and navigate to the attacker directory:

```bash
cd dictionary_attack/attacker
python3 dictionary_attacker.py --host 127.0.0.1 --port 8080 --username admin --src-ip 192.168.1.100 --wordlist wordlist.txt
```

**Command-line options:**
- `--host`: Target host (default: 127.0.0.1)
- `--port`: Target port (default: 8080)
- `--username`: Target username (default: admin)
- `--src-ip`: Source IP for packet simulation (default: 192.168.1.100)
- `--wordlist`: Password dictionary file (default: wordlist.txt)

## Attack Features

### Packet-Level Analysis:
- **IP Header Logging**: Version, IHL, TOS, Total Length, ID, Flags, TTL, Protocol, Checksum, Source/Dest IPs
- **TCP Header Logging**: Source/Dest Ports, Sequence/ACK numbers, Data Offset, Flags (SYN/ACK/PSH/etc), Window, Checksum, Urgent Pointer
- **HTTP Payload Analysis**: Complete request/response logging with payload lengths
- **Real-time Packet Simulation**: Shows what raw packets would contain without requiring root privileges

### Attacker Capabilities:
- Loads password dictionary from wordlist.txt
- Crafts HTTP POST requests with variable headers
- Detailed packet construction simulation and logging
- Randomizes User-Agent headers for stealth
- Implements variable delays between attempts
- Tracks response times and success rates
- Generates comprehensive attack logs with packet details
- Shows real-time progress and network-level statistics

### Victim Server Features:
- Simulates realistic authentication system
- Stores user credentials with hashed passwords
- Logs all authentication attempts with timestamps
- Tracks failed attempts per IP address
- Provides detailed statistics and monitoring
- Responds with realistic HTTP status codes

## Attack Analysis

The simulation demonstrates:

1. **Password Dictionary**: Contains common passwords and variations
2. **Brute Force Method**: Systematic testing of each password
3. **HTTP Protocol**: Uses standard web authentication methods
4. **Stealth Techniques**: Variable timing and headers to avoid detection
5. **Success Detection**: Analyzes server responses to identify successful login

## Educational Objectives

This simulation helps understand:
- How dictionary attacks work in practice
- The importance of strong, unique passwords
- Server-side logging and monitoring capabilities
- Rate limiting and detection mechanisms
- Attack patterns and defense strategies

## Defense Mechanisms

Potential countermeasures demonstrated:
- Account lockout after failed attempts
- Rate limiting per IP address
- Logging and monitoring of failed attempts
- Strong password policies
- Multi-factor authentication (conceptual)

## Sample Output

### Packet-Level Attacker Output:
```
============================================
[*] ATTEMPT #1: admin:password
============================================
[*] Establishing TCP connection to 127.0.0.1:8080
[*] Simulated packet construction:
[SIMULATED SEND] Packet Details:
[SEND] IP Header:
    Version: 4, IHL: 5, TOS: 0
    Total Length: 245, ID: 12345
    Flags: 0, Fragment Offset: 0
    TTL: 64, Protocol: 6, Checksum: 0x1234
    Source IP: 192.168.1.100, Destination IP: 127.0.0.1
[SEND] TCP Header:
    Source Port: 54321, Destination Port: 8080
    Sequence: 12345, Acknowledgment: 67890
    Data Offset: 5, Flags: PSH|ACK (0x18)
    Window: 8192, Checksum: 0x5678, Urgent Pointer: 0
    Payload Length: 205
    HTTP Request: POST /login (user: admin, pass: password)

[*] Sending actual HTTP request via TCP socket...
[SIMULATED RECV] Response packet details:
[RECV] IP Header:
    Version: 4, IHL: 5, TOS: 0
    Total Length: 419, ID: 54321
    Source IP: 127.0.0.1, Destination IP: 192.168.1.100
[RECV] TCP Header:
    Source Port: 8080, Destination Port: 54321
    Flags: PSH|ACK (0x18)
    Payload Length: 379

[-] Failed attempt 1: admin:password (Response time: 0.123s)

[+] SUCCESS! Found password: secret (Response time: 0.087s)
```

### Victim Server Output:
```
[2024-07-25 14:30:15] 127.0.0.1 - admin:password - FAILED
[2024-07-25 14:30:16] 127.0.0.1 - admin:123456 - FAILED
[2024-07-25 14:30:17] 127.0.0.1 - admin:secret - SUCCESS
```

## Log Files

The attack generates detailed log files:
- `dictionary_attack_log_YYYYMMDD_HHMMSS.txt`

Contains:
- Attack configuration and timeline
- Detailed attempt log with response times
- Success/failure analysis
- Pattern recognition results

## Troubleshooting

### "Address already in use" Error

If the victim server shows port 8080 is already in use:

```bash
# From project root directory
./cleanup.sh    # Clean up existing processes
./start.sh      # Restart simulation
```

Or manually:
```bash
# Find and kill process using port 8080
lsof -i :8080
kill <PID>

# Restart victim server
cd dictionary_attack/victim
python3 auth_server.py --docker
```

### Attacker Can't Connect

1. Make sure victim server started successfully
2. Check if firewall is blocking connections
3. Verify correct IP address and port in command

## Important Notes

⚠️ **Educational Use Only**: This simulation is designed for educational and defensive security research purposes only.

⚠️ **Ethical Considerations**: Only use this simulation on systems you own or have explicit permission to test.

⚠️ **VM Environment**: Run in isolated virtual machines to prevent accidental network interference.

## Learning Outcomes

After running this simulation, you should understand:
1. How dictionary attacks systematically test common passwords
2. The importance of using strong, unique passwords
3. How server logging can detect and track attack attempts
4. The effectiveness of rate limiting and account lockout mechanisms
5. Why password complexity requirements exist in modern systems