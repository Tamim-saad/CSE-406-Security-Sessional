# Password Attack Simulations - CSE 406 Project

Educational cybersecurity simulation demonstrating two password attack methods for defensive security research and countermeasure development.

## Project Overview

This project implements and demonstrates two distinct password attack methodologies with packet-level analysis, designed for educational purposes to understand attack vectors and develop effective countermeasures.

### Implemented Attack Types

#### 1. Dictionary Attack
- **Method**: High-volume brute force using common password dictionaries
- **Implementation**: Raw socket packet construction with TCP/IP header analysis
- **Target**: Port 8080 with generic user accounts
- **Detection Profile**: Easy to detect (high volume, many failed attempts)
- **Speed**: Fast execution (100+ attempts/minute)
- **Wordlist**: 5,530+ common passwords

#### 2. Known Password Attack (OSINT-Based)
- **Method**: Intelligence-driven targeted attack using personal information
- **Implementation**: OSINT data collection with human-like behavior simulation
- **Target**: Port 8081 with realistic user profiles
- **Detection Profile**: Difficult to detect (low volume, targeted attempts)
- **Speed**: Slow, human-like timing (0.5-2.0s delays)
- **Intelligence**: Personal data patterns (names, birth years, pets, locations)

## Quick Start - One Command Launch

```bash
cd /home/pridesys/Desktop/extra/attack/project
./start.sh
```

This launches **4 interactive terminals** for complete attack simulation:
- Dictionary Attack Server + Client (with packet-level analysis)
- Known Password Attack Server + Client (with OSINT + packet-level analysis)

### If Ports Are Busy

If you see "Address already in use" errors:

```bash
./cleanup.sh    # Clean up any existing processes
./start.sh      # Start fresh simulation
```

## Technical Implementation Details

### Dictionary Attack Features
- **Packet-level logging**: Complete TCP/IP header construction and analysis
- **HTTP POST simulation**: Realistic web authentication attempts
- **Variable timing**: Configurable delays to simulate different attack speeds
- **Comprehensive logging**: Response time analysis and success tracking
- **User-Agent rotation**: Multiple browser signatures for stealth

### Known Password Attack Features
- **OSINT simulation**: Realistic personal information gathering
- **Pattern generation**: 20+ password pattern algorithms based on personal data
- **Stealth techniques**: Human-like timing and behavior patterns
- **Intelligence analysis**: Pattern matching and success correlation
- **Targeted profiles**: 5 realistic user accounts with personal information

### Victim Server Capabilities
- **Multi-threaded handling**: Concurrent attack simulation support
- **Real-time logging**: Live attack attempt monitoring
- **Pattern analysis**: Detection of personal information usage in passwords
- **Statistics tracking**: Comprehensive attack metrics and success rates
- **Response simulation**: Realistic HTTP responses for success/failure

## Attack Demonstration Results

### Dictionary Attack Results
- **Success Rate**: High success against weak passwords
- **Detection**: Easily detected due to high volume
- **Time to Success**: Fast when password is in dictionary
- **Log Generation**: Extensive packet-level logs for analysis

### Known Password Attack Results
- **Success Rate**: High success against personal information passwords
- **Detection**: Low detection probability due to human-like behavior
- **Intelligence Gathering**: Successful OSINT simulation
- **Pattern Effectiveness**: Personal data patterns highly effective

## Countermeasures Implemented

### 1. Rate Limiting Detection
- **Monitoring**: Failed attempt frequency tracking
- **Threshold**: Configurable attempt limits per IP
- **Response**: HTTP 429 rate limiting responses

### 2. Pattern Analysis
- **Detection**: Personal information usage in password attempts
- **Logging**: Detailed pattern analysis in attack logs
- **Intelligence**: Attack pattern correlation and analysis

### 3. Behavioral Analysis
- **Timing**: Attack timing pattern analysis
- **Volume**: Request volume monitoring
- **Source**: IP-based attack tracking

## Detailed Instructions

See **`ATTACK-SIMULATION-GUIDE.md`** for complete step-by-step simulation instructions.

## Files Structure

```
attack/
├── start.sh                           # One-command launcher
├── cleanup.sh                         # Process cleanup utility
├── ATTACK-SIMULATION-GUIDE.md         # Complete simulation guide
├── dictionary_attack/
│   ├── attacker/
│   │   ├── dictionary_attacker.py     # Main dictionary attack implementation
│   │   ├── wordlist.txt              # 5,530+ password dictionary
│   │   └── test_wordlist.txt         # Smaller test dictionary
│   ├── victim/
│   │   └── auth_server.py            # Dictionary attack victim server
│   └── ss/                           # Screenshot documentation
│       ├── Pasted image.png          # Server startup
│       ├── Pasted image (2).png      # Attacker initialization
│       ├── Pasted image (3).png      # Attack execution
│       ├── Pasted image (4).png      # Success demonstration
│       └── Pasted image (5).png      # Results analysis
├── known_password_attack/
│   ├── attacker/
│   │   └── known_password_attacker.py # OSINT-based attack implementation
│   ├── victim/
│   │   └── auth_server.py            # Known password victim server
│   └── ss/                           # Screenshot documentation
│       ├── Pasted image.png          # Server with user profiles
│       ├── Pasted image (2).png      # OSINT attack initialization
│       ├── Pasted image (3).png      # Intelligence gathering
│       └── Pasted image (4).png      # Attack execution results
├── kathara-lab/                       # Network simulation environment
│   ├── lab.conf                      # Network configuration
│   ├── dict_attacker/                # Dictionary attacker node
│   ├── dict_victim/                  # Dictionary victim node
│   ├── known_attacker/               # Known password attacker node
│   └── known_victim/                 # Known password victim node
└── docker-setup/                     # Containerization support
    ├── docker-compose.yml            # Multi-container setup
    └── Dockerfile.base               # Base container image
```

## Research Findings

### Attack Effectiveness
1. **Dictionary attacks** are highly effective against common passwords but easily detectable
2. **OSINT-based attacks** show high success rates against personal information passwords
3. **Packet-level analysis** provides detailed forensic capabilities for attack investigation
4. **Human-like timing** significantly reduces detection probability

### Defense Effectiveness
1. **Rate limiting** effectively counters high-volume dictionary attacks
2. **Pattern analysis** can detect personal information usage in passwords
3. **Behavioral monitoring** helps identify suspicious login patterns
4. **Multi-layered defense** provides comprehensive protection

## Educational Value

This simulation provides hands-on experience with:
- Password attack methodologies and implementation
- Network packet analysis and forensics
- OSINT techniques and personal information exploitation
- Defensive countermeasure development and testing
- Real-world cybersecurity threat understanding

## Ethical Use Statement

⚠️ **Authorized systems only** - For cybersecurity education and defensive research

This project is developed exclusively for:
- Educational cybersecurity training
- Defensive security research
- Countermeasure development and testing
- Academic understanding of attack vectors

**Course**: CSE 406 - Computer Security (BUET)  
**Team**: Tamim Hasan Saad (2005095), Habiba Rafique (2005096)  
**Academic Year**: 2025