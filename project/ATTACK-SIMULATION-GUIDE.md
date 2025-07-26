# Password Attack Simulation - Complete Guide

## Step 1: Launch Simulation

**Run this command:**
```bash
cd /home/pridesys/Desktop/extra/attack
./start.sh
```

**Result:** 4 terminal windows will open automatically
- ✅ Dictionary Attack Server (Port 8080)
- ✅ Dictionary Attacker
- ✅ Known Password Attack Server (Port 8081)  
- ✅ Known Password Attacker

---

## Step 2: Configure Each Terminal

You need to interact with each terminal in this order:

### Terminal 1: Dictionary Attack Server (Port 8080)
**What you see:**
```
=== Dictionary Attack Victim Server ===
Starting authentication server on port 8080...

Enter server host (default: 127.0.0.1): [PRESS ENTER]
Enter server port (default: 8080): [PRESS ENTER]

Available test accounts:
- admin:secret
- user:password123
- test:test123
- root:toor
- guest:guest

Server starting on 127.0.0.1:8080
Waiting for connections...
```

**What to do:**
1. Press **Enter** twice (accept defaults)
2. Server will start and show available accounts
3. **Keep this window open** - it will show incoming attack attempts

---

### Terminal 2: Dictionary Attacker
**What you see:**
```
=== Dictionary Attack Client ===
Starting dictionary attack...

Target host (default: 127.0.0.1): [ENTER IP ADDRESS]
Target port (default: 8080): [PRESS ENTER]
Target username: [ENTER USERNAME]
```

**What to do:**
1. **Target host**: Enter `127.0.0.1` (or press Enter for default)
2. **Target port**: Press **Enter** (uses 8080)
3. **Target username**: Enter `admin` (or any user from server list)
4. **Watch the attack**: Attacker will systematically try passwords

**Example output:**
```
[+] Loaded 15 passwords from wordlist
[*] Starting dictionary attack on 127.0.0.1:8080
[*] Target username: admin

[1/15] Trying: password → FAILED
[2/15] Trying: 123456 → FAILED
[3/15] Trying: admin → FAILED
[4/15] Trying: secret → SUCCESS!

[SUCCESS] Password found: admin:secret
Attack completed in 2.3 seconds
Success rate: 26.7% (4/15 attempts)
```

---

### Terminal 3: Known Password Server (Port 8081)
**What you see:**
```
=== Known Password Attack Victim Server ===
Starting user profile server on port 8081...

Enter server host (default: 127.0.0.1): [PRESS ENTER]
Enter server port (default: 8081): [PRESS ENTER]

Available user profiles:
- john.smith (Password pattern: Personal info based)
- sarah.jones (Password pattern: Pet name + year)
- mike.johnson (Password pattern: City + birth year)

Server starting on 127.0.0.1:8081
```

**What to do:**
1. Press **Enter** twice (accept defaults)
2. Server shows user profiles with personal information
3. **Keep this window open** - it will show targeted attack attempts

---

### Terminal 4: Known Password Attacker
**What you see:**
```
=== Known Password Attack Client ===
Starting OSINT-based attack...

Target host (default: 127.0.0.1): [ENTER IP ADDRESS]
Target port (default: 8081): [PRESS ENTER]
Target username: [ENTER USERNAME]
Max attempts (default: 20): [PRESS ENTER]
```

**What to do:**
1. **Target host**: Enter `127.0.0.1`
2. **Target port**: Press **Enter** (uses 8081)
3. **Target username**: Enter `john.smith` (or any user from server)
4. **Max attempts**: Press **Enter** (uses 20)
5. **Watch OSINT attack**: Attacker generates passwords from personal info

**Example output:**
```
[*] Gathering intelligence on target: john.smith

Target Profile:
- Full name: John Smith
- Birth year: 1985
- Pet name: Buddy  
- Hometown: Boston

[*] Generating targeted passwords...
Generated 25 password candidates based on personal information

[1/25] Trying: John1985! → SUCCESS!

[SUCCESS] Password cracked: john.smith:John1985!
Attack completed in 0.8 seconds
OSINT effectiveness: 96% (minimal attempts needed)
```

---

## Attack Comparison

### Dictionary Attack Characteristics:
- **Method**: Brute force with common passwords
- **Speed**: Fast (100+ attempts/minute)
- **Success Rate**: Low-Medium (depends on password strength)
- **Detection**: Easy to detect (many failed attempts)
- **Use Case**: General password cracking

### Known Password Attack Characteristics:
- **Method**: Personal information-based targeting
- **Speed**: Slow (human-like timing)
- **Success Rate**: High (when personal info available)
- **Detection**: Hard to detect (few attempts)
- **Use Case**: Targeted individual attacks

---

## What to Observe

### In Dictionary Attack:
1. **Server Terminal**: Shows rapid incoming attempts
2. **Attacker Terminal**: Shows systematic password testing
3. **Pattern**: High volume, predictable sequence
4. **Detection**: Many failed login attempts from same IP

### In Known Password Attack:
1. **Server Terminal**: Shows few, spaced-out attempts
2. **Attacker Terminal**: Shows intelligence gathering phase
3. **Pattern**: Low volume, targeted guesses
4. **Detection**: Appears like normal failed logins

---

## Educational Objectives

This simulation demonstrates:

1. **Attack Vector Differences**: Volume vs Intelligence-based approaches
2. **Detection Challenges**: High-volume vs stealthy attacks
3. **Defense Strategies**: Rate limiting, account lockout, monitoring
4. **Real-world Applications**: Understanding actual attack patterns

---

## Stopping the Simulation

- **Simple**: Close all terminal windows
- **Or**: Press `Ctrl+C` in each terminal
- **Clean up**: `pkill -f "python3.*auth_server\|dictionary_attacker\|known_password_attacker"`

---

## Security Notes

⚠️ **Educational Purpose Only**: This simulation is for learning cybersecurity defense

⚠️ **Authorized Systems Only**: Only use on systems you own or have permission

⚠️ **Defensive Focus**: Understanding attacks to build better defenses