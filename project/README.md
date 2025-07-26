# Password Attack Simulations - CSE 406 Project

Educational cybersecurity simulation demonstrating two password attack methods for defensive security research.

## Quick Start - One Command Launch

```bash
cd /home/pridesys/Desktop/extra/attack
./start.sh
```

This launches **4 interactive terminals** for complete attack simulation:
- Dictionary Attack Server + Client
- Known Password Attack Server + Client

## Attack Types

### 1. Dictionary Attack
- **Method**: Volume-based brute force with common passwords
- **Speed**: Fast (100+ attempts/minute)  
- **Detection**: Easy (many failed attempts)

### 2. Known Password Attack
- **Method**: Intelligence-driven using personal information
- **Speed**: Slow (human-like timing)
- **Detection**: Difficult (few targeted attempts)

## Detailed Instructions

See **`ATTACK-SIMULATION-GUIDE.md`** for complete step-by-step simulation instructions.

## Files Structure

```
attack/
├── start.sh                           # One-command launcher
├── ATTACK-SIMULATION-GUIDE.md         # Complete simulation guide
├── dictionary_attack/
│   ├── attacker/dictionary_attacker.py
│   ├── attacker/wordlist.txt
│   └── victim/auth_server.py
└── known_password_attack/
    ├── attacker/known_password_attacker.py
    └── victim/auth_server.py
```

## Educational Purpose

⚠️ **Authorized systems only** - For cybersecurity education and defensive research

**Course**: CSE 406 - Computer Security (BUET)  
**Team**: Tamim Hasan Saad (2005095), Habiba Rafique (2005096)