# Known Password Attack Simulation with Packet-Level Analysis

This directory contains the implementation of a Known Password Attack simulation with detailed TCP/IP packet logging for educational and defensive security purposes.

## Overview

A Known Password Attack uses personal information about the target (gathered through OSINT - Open Source Intelligence) to generate highly targeted password guesses. This implementation includes comprehensive packet-level analysis showing IP headers, TCP headers, and HTTP payload details, combined with OSINT-based password generation for educational network security analysis.

## Files Structure

```
known_password_attack/
├── attacker/
│   └── known_password_attacker.py    # Main attacker script with OSINT
├── victim/
│   └── auth_server.py                # Authentication server with user profiles
└── README.md                         # This file
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
cd known_password_attack/victim
python3 auth_server.py --docker
```

The server will start on `0.0.0.0:8081` and display user profiles with personal information patterns:

- **john.smith**: John1985! (FirstName + BirthYear + Special)
- **sarah.jones**: Luna2024 (PetName + CurrentYear)  
- **mike.johnson**: Chicago78! (Hometown + BirthYear + Special)
- **anna.wilson**: Bella@90 (PetName + BirthYear(suffix) + Special)
- **david.brown**: Dolphins83 (FavoriteTeam + BirthYear)

#### Step 2: Run the Packet-Level Attacker

Open another terminal and navigate to the attacker directory:

```bash
cd known_password_attack/attacker
python3 known_password_attacker.py --host 127.0.0.1 --port 8081 --username john.smith --src-ip 192.168.1.101 --max-attempts 15
```

**Command-line options:**
- `--host`: Target host (default: 127.0.0.1)
- `--port`: Target port (default: 8081)
- `--username`: Target username (required - use one of the users above)
- `--src-ip`: Source IP for packet simulation (default: 192.168.1.101)
- `--max-attempts`: Maximum attempts (default: 20)
- `--delay-min`: Minimum delay between attempts (default: 0.5)
- `--delay-max`: Maximum delay between attempts (default: 2.0)

## Attack Features

### Packet-Level Analysis:
- **IP Header Logging**: Version, IHL, TOS, Total Length, ID, Flags, TTL, Protocol, Checksum, Source/Dest IPs
- **TCP Header Logging**: Source/Dest Ports, Sequence/ACK numbers, Data Offset, Flags (SYN/ACK/PSH/etc), Window, Checksum, Urgent Pointer  
- **HTTP Payload Analysis**: Complete request/response logging with payload lengths
- **OSINT Pattern Logging**: Shows which personal information patterns are being tested
- **Real-time Packet Simulation**: Shows what raw packets would contain without requiring root privileges

### Intelligence Gathering (OSINT Simulation):
- Simulates gathering personal information from social media/public records
- Collects: Full name, birth year, pet names, hometown, favorite teams, employer
- Analyzes: Common numbers, interests, personal patterns
- Shows realistic OSINT intelligence gathering process

### Password Generation Engine:
- **Pattern 1**: FirstName + BirthYear + Special (!@#$*)
- **Pattern 2**: PetName + CurrentYear/BirthYear
- **Pattern 3**: Hometown + BirthYear + Special
- **Pattern 4**: FavoriteTeam + BirthYear
- **Pattern 5**: Company + BirthYear
- **Pattern 6**: FirstName + LastName + Numbers
- **Pattern 7**: Common variations with 123, 1234
- **Pattern 8**: Pet + Special characters
- **Pattern 9**: Birth date variations
- **Pattern 10**: Team + common numbers

### Stealth Features:
- Limited attempts to avoid account lockout
- Human-like delays between attempts (0.5-2.0 seconds)
- Randomized User-Agent headers
- Pattern analysis and success tracking

### Victim Server Features:
- Realistic user profiles with personal information
- Pattern detection in attempted passwords
- Real-time analysis of personal information usage
- Comprehensive logging with pattern recognition
- Statistical analysis of attack methods

## Sample Attack Flow

### 1. Intelligence Gathering Phase:
```
[*] Gathering intelligence on target: john.smith
[*] Simulating OSINT (Open Source Intelligence) collection...
[+] Intelligence gathered successfully!
    Full Name: John Smith
    Birth Year: 1985
    Pet Name: Buddy
    Hometown: Boston
    Favorite Team: Patriots
    Company: TechCorp
```

### 2. Password Generation Phase:
```
[*] Generating personalized password candidates...
[+] Generated 45 password candidates
[*] Top password candidates:
     1. John1985!
     2. John85!
     3. Buddy2024
     4. Buddy1985
     5. Boston1985!
     6. Patriots1985
     7. TechCorp1985
    ... and 38 more
```

### 3. Packet-Level Attack Execution:
```
======================================================================
[*] OSINT-BASED ATTEMPT #3: john.smith:Buddy2024
======================================================================
[*] Password pattern: PetName + CurrentYear
[*] Establishing TCP connection to 127.0.0.1:8081
[*] Simulated packet construction:
[SIMULATED SEND] Packet Details:
[SEND] IP Header:
    Version: 4, IHL: 5, TOS: 0
    Total Length: 563, ID: 58111
    Flags: 0, Fragment Offset: 0
    TTL: 64, Protocol: 6, Checksum: 0x54b7
    Source IP: 192.168.1.101, Destination IP: 127.0.0.1
[SEND] TCP Header:
    Source Port: 34275, Destination Port: 8081
    Sequence: 11494, Acknowledgment: 49684
    Data Offset: 5, Flags: PSH|ACK (0x18)
    Window: 8192, Checksum: 0x6c4e, Urgent Pointer: 0
    Payload Length: 523
    HTTP Request: POST /login (user: john.smith, pass: Buddy2024)
    OSINT Pattern: PetName + CurrentYear

[*] Sending actual OSINT-based HTTP request via TCP socket...
[SIMULATED RECV] Response packet details:
[RECV] IP Header:
    Version: 4, IHL: 5, TOS: 0
    Total Length: 459, ID: 58490
    Source IP: 127.0.0.1, Destination IP: 192.168.1.101
[RECV] TCP Header:
    Source Port: 8081, Destination Port: 31724
    Flags: PSH|ACK (0x18)
    Payload Length: 419

[-] Failed attempt 3: Buddy2024 (Pattern: PetName + CurrentYear)

[+] SUCCESS! Password found: John1985!
[+] Pattern used: FirstName + BirthYear + Special
[+] Response time: 0.234s
```

### 4. Victim Server Analysis:
```
[2024-07-25 14:45:12] 127.0.0.1 - john.smith:John123 - FAILED [Contains: FirstName]
[2024-07-25 14:45:15] 127.0.0.1 - john.smith:Buddy2024 - FAILED [Contains: PetName]
[2024-07-25 14:45:18] 127.0.0.1 - john.smith:John1985! - SUCCESS [Contains: FirstName, BirthYear]
```

## Attack Analysis Features

### Pattern Recognition:
- Tracks which personal information patterns are used
- Analyzes success rates of different pattern types
- Identifies most effective OSINT-based approaches

### Comprehensive Logging:
- Detailed intelligence gathering results
- All generated password candidates
- Attempt-by-attempt analysis with patterns
- Response time measurements
- Success/failure statistics

## Educational Objectives

This simulation demonstrates:

1. **OSINT Techniques**: How personal information is gathered and weaponized
2. **Psychology of Passwords**: Why people use personal information in passwords
3. **Targeted Attacks**: Difference between generic and personalized attacks
4. **Social Engineering**: How personal details become security vulnerabilities
5. **Pattern Analysis**: Common human password creation behaviors

## Defense Mechanisms

The simulation illustrates these defenses:

1. **Account Lockout**: Limited attempts prevent unlimited guessing
2. **Rate Limiting**: Delays between attempts slow down attacks
3. **Pattern Detection**: Server recognizes personal information usage
4. **Monitoring**: Real-time analysis of attack patterns
5. **Strong Password Policies**: Avoiding personal information in passwords

## Real-World OSINT Sources

In actual attacks, information might come from:
- Social media profiles (Facebook, LinkedIn, Twitter)
- Public records and databases
- Company websites and directories
- News articles and press releases
- Data breaches and leaked information
- Professional networking sites

## Sample Attack Results

### Successful Attack Log:
```
Known Password Attack Summary
=====================================
Target: 127.0.0.1:8081
Username: john.smith
Intelligence Gathering: Successful
Attack duration: 23.45 seconds
Total attempts: 4
Password candidates generated: 45

[+] ATTACK SUCCESSFUL!
[+] Valid credentials found: john.smith:John1985!
[+] Password cracked on attempt #4
[+] Pattern used: FirstName + BirthYear + Special
[+] Time to success: 5.86 seconds

Pattern Analysis:
  FirstName + BirthYear + Special: 1 attempts
  PetName: 1 attempts
  PetName + CurrentYear: 1 attempts
  FirstName + CommonNumbers: 1 attempts
```

## Important Security Lessons

### For Users:
1. **Avoid Personal Information**: Don't use names, birthdates, or pet names in passwords
2. **Limit Social Media Exposure**: Be cautious about personal information shared online
3. **Use Random Passwords**: Password managers generate truly random passwords
4. **Enable 2FA**: Multi-factor authentication prevents password-only attacks

### For Organizations:
1. **Employee Training**: Educate about social engineering and OSINT risks
2. **Password Policies**: Enforce rules against personal information usage
3. **Account Monitoring**: Detect unusual login patterns and failed attempts
4. **Incident Response**: Have procedures for handling potential compromises

## Troubleshooting

### "Address already in use" Error

If the victim server shows port 8081 is already in use:

```bash
# From project root directory
./cleanup.sh    # Clean up existing processes
./start.sh      # Restart simulation
```

Or manually:
```bash
# Find and kill process using port 8081
lsof -i :8081
kill <PID>

# Restart victim server
cd known_password_attack/victim
python3 auth_server.py --docker
```

### No Password Candidates Generated

1. Make sure you're using a valid username from the target profiles
2. Check that the username matches exactly (case-sensitive): `john.smith`, `sarah.jones`, etc.
3. Available usernames are shown when the victim server starts

### Attacker Can't Connect

1. Ensure victim server started successfully on port 8081
2. Verify the username parameter is provided: `--username john.smith`
3. Check network connectivity between terminals

## Ethical Considerations

⚠️ **Educational Use Only**: This simulation is for learning about cybersecurity threats.

⚠️ **Legal Compliance**: Only test on systems you own or have explicit written permission to test.

⚠️ **Privacy Respect**: In real-world security testing, always respect privacy and follow ethical guidelines.

⚠️ **Responsible Disclosure**: If you discover vulnerabilities, report them responsibly.

## Learning Outcomes

After completing this simulation, you should understand:

1. How personal information becomes a security vulnerability
2. The effectiveness of targeted vs. generic password attacks
3. The importance of strong, non-personal passwords
4. How OSINT gathering works in cybersecurity contexts
5. Why privacy protection and information security go hand-in-hand
6. The role of behavioral analysis in both attacks and defenses