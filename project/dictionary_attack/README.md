# Dictionary Attack Simulation

This directory contains the implementation of a Dictionary Attack simulation for educational and defensive security purposes.

## Overview

A Dictionary Attack is a brute-force attack method where an attacker systematically tries passwords from a predefined list (dictionary) of commonly used passwords. This attack exploits weak password choices by users.

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

### Step 1: Start the Victim Server

Open a terminal and navigate to the victim directory:

```bash
cd dictionary_attack/victim
python3 auth_server.py
```

The server will start on `127.0.0.1:8080` by default and display available user accounts:
- admin:secret
- user:password123
- test:test123
- root:toor
- guest:guest

### Step 2: Run the Attacker

Open another terminal and navigate to the attacker directory:

```bash
cd dictionary_attack/attacker
python3 dictionary_attacker.py
```

Follow the prompts to configure the attack:
- Target host (default: 127.0.0.1)
- Target port (default: 8080)
- Target username (default: admin)

## Attack Features

### Attacker Capabilities:
- Loads password dictionary from wordlist.txt
- Crafts HTTP POST requests with variable headers
- Randomizes User-Agent headers for stealth
- Implements variable delays between attempts
- Tracks response times and success rates
- Generates comprehensive attack logs
- Shows real-time progress and statistics

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

### Attacker Output:
```
[*] Starting dictionary attack against 127.0.0.1:8080
[*] Target username: admin
[*] Dictionary size: 154 passwords
[*] Progress: 6.5% (10/154)
[-] Failed attempt 10: admin:password (Response time: 0.123s)
[+] SUCCESS! Found password: secret (Response time: 0.087s)
[+] Password cracked on attempt #15
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