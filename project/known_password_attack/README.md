# Known Password Attack Simulation

This directory contains the implementation of a Known Password Attack simulation for educational and defensive security purposes.

## Overview

A Known Password Attack uses personal information about the target (gathered through OSINT - Open Source Intelligence) to generate highly targeted password guesses. This attack exploits human tendencies to use personal information in passwords.

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

### Step 1: Start the Victim Server

Open a terminal and navigate to the victim directory:

```bash
cd known_password_attack/victim
python3 auth_server.py
```

The server will start on `127.0.0.1:8081` by default and display user profiles with personal information patterns:

- **john.smith**: John1985! (FirstName + BirthYear + Special)
- **sarah.jones**: Luna2024 (PetName + CurrentYear)  
- **mike.johnson**: Chicago78! (Hometown + BirthYear + Special)
- **anna.wilson**: Bella@90 (PetName + BirthYear(suffix) + Special)
- **david.brown**: Dolphins83 (FavoriteTeam + BirthYear)

### Step 2: Run the Attacker

Open another terminal and navigate to the attacker directory:

```bash
cd known_password_attack/attacker
python3 known_password_attacker.py
```

Follow the prompts to configure the attack:
- Target host (default: 127.0.0.1)
- Target port (default: 8081)
- Target username (required - use one of the users above)
- Maximum attempts (default: 20)
- Delay range (default: 0.5-2.0 seconds)

## Attack Features

### Intelligence Gathering (OSINT Simulation):
- Simulates gathering personal information from social media/public records
- Collects: Full name, birth year, pet names, hometown, favorite teams, employer
- Analyzes: Common numbers, interests, personal patterns

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

### 3. Attack Execution:
```
[*] Progress: 15.0% (3/20)
[-] Failed attempt 3: john.smith:Buddy2024 (Pattern: PetName + CurrentYear)
[*] Progress: 20.0% (4/20)
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