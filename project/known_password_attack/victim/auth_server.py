#!/usr/bin/env python3

import socket
import threading
import hashlib
import time
from urllib.parse import unquote_plus

class KnownPasswordAuthServer:
    def __init__(self, host="127.0.0.1", port=8081):
        self.host = host
        self.port = port
        self.users_db = {}
        self.attempt_log = []
        self.failed_attempts = {}
        self.running = False
        
        # Initialize realistic user profiles for known password attack
        self.initialize_user_profiles()
        
    def initialize_user_profiles(self):
        """Initialize John Smith profile with dynamic password configuration"""
        print("[*] Known Password Attack Victim Server Configuration")
        print("="*70)
        
        # John Smith's personal information (public/OSINT data)
        john_smith_info = {
            "full_name": "John Smith",
            "first_name": "John",
            "last_name": "Smith",
            "birth_year": "1985",
            "birth_date": "15031985",  # 15th March 1985
            "age": "39",
            "pet_name": "Buddy",
            "hometown": "Boston",
            "favorite_team": "Patriots",
            "company": "TechCorp",
            "interests": ["technology", "football", "gaming"]
        }
        
        print("Target Profile: John Smith (john.smith)")
        print("Personal Information Available (OSINT):")
        print(f"  Full Name: {john_smith_info['full_name']}")
        print(f"  Birth Year: {john_smith_info['birth_year']} (Age: {john_smith_info['age']})")
        print(f"  Pet Name: {john_smith_info['pet_name']}")
        print(f"  Hometown: {john_smith_info['hometown']}")
        print(f"  Favorite Team: {john_smith_info['favorite_team']}")
        print(f"  Company: {john_smith_info['company']}")
        print(f"  Interests: {', '.join(john_smith_info['interests'])}")
        print()
        
        # Get password configuration from user
        try:
            password = input(f"Enter John Smith's password: ").strip()
            if not password:
                print("[!] Password cannot be empty!")
                return self.initialize_user_profiles()
            
            # Analyze the password pattern
            pattern = self.analyze_password_pattern(password, john_smith_info)
            
            # Create user account
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            self.users_db["john.smith"] = {
                "password_hash": password_hash,
                "plain_password": password,  # For simulation purposes only
                "personal_info": john_smith_info,
                "password_pattern": pattern,
                "login_attempts": 0,
                "successful_logins": 0
            }
            
            print(f"[*] Password configured for john.smith: {password}")
            print(f"[*] Detected pattern: {pattern}")
            print(f"[*] Password hash: {password_hash[:16]}...")
            
        except (EOFError, KeyboardInterrupt):
            # Fallback for automated environments
            print("\n[*] Using default configuration for automated environment")
            password = "John1985!"
            pattern = "FirstName + BirthYear + Special"
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            self.users_db["john.smith"] = {
                "password_hash": password_hash,
                "plain_password": password,
                "personal_info": john_smith_info,
                "password_pattern": pattern,
                "login_attempts": 0,
                "successful_logins": 0
            }
            print(f"[*] Password configured for john.smith: {password}")
            print(f"[*] Detected pattern: {pattern}")
    
    def analyze_password_pattern(self, password, personal_info):
        """Analyze what personal information patterns the password contains"""
        patterns = []
        
        # Check for personal information in password
        if personal_info['first_name'].lower() in password.lower():
            patterns.append("FirstName")
        if personal_info['last_name'].lower() in password.lower():
            patterns.append("LastName")
        if personal_info['birth_year'] in password:
            patterns.append("BirthYear")
        elif personal_info['birth_year'][-2:] in password:
            patterns.append("BirthYear(short)")
        if personal_info['pet_name'].lower() in password.lower():
            patterns.append("PetName")
        if personal_info['hometown'].lower() in password.lower():
            patterns.append("Hometown")
        if personal_info['favorite_team'].lower() in password.lower():
            patterns.append("FavoriteTeam")
        if personal_info['company'].lower() in password.lower():
            patterns.append("Company")
        if any(c in password for c in "!@#$*"):
            patterns.append("Special")
        if "2024" in password or "2025" in password:
            patterns.append("CurrentYear")
        if any(num in password for num in ["123", "1234", "12345"]):
            patterns.append("CommonNumbers")
        
        return " + ".join(patterns) if patterns else "Unknown/Custom"
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_user(self, username, password):
        """Authenticate user credentials"""
        if username not in self.users_db:
            return False
            
        password_hash = self.hash_password(password)
        stored_hash = self.users_db[username]["password_hash"]
        
        # Update attempt counter
        self.users_db[username]["login_attempts"] += 1
        
        if password_hash == stored_hash:
            self.users_db[username]["successful_logins"] += 1
            return True
        
        return False
    
    def log_attempt(self, client_ip, username, password, success):
        """Log authentication attempt with detailed analysis"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Analyze password pattern if user exists
        pattern_analysis = ""
        if username in self.users_db:
            user_info = self.users_db[username]["personal_info"]
            
            # Check if password contains personal information
            contains_name = user_info["full_name"].lower().split()[0].lower() in password.lower()
            contains_birth_year = user_info["birth_year"] in password
            contains_pet = user_info["pet_name"].lower() in password.lower()
            contains_hometown = user_info["hometown"].lower() in password.lower()
            contains_team = user_info["favorite_team"].lower() in password.lower()
            
            patterns = []
            if contains_name:
                patterns.append("FirstName")
            if contains_birth_year:
                patterns.append("BirthYear")
            if contains_pet:
                patterns.append("PetName")
            if contains_hometown:
                patterns.append("Hometown")
            if contains_team:
                patterns.append("FavoriteTeam")
            
            if patterns:
                pattern_analysis = f" [Contains: {', '.join(patterns)}]"
        
        attempt = {
            "timestamp": timestamp,
            "client_ip": client_ip,
            "username": username,
            "password": password,
            "success": success,
            "pattern_analysis": pattern_analysis
        }
        
        self.attempt_log.append(attempt)
        
        # Track failed attempts per IP
        if not success:
            if client_ip not in self.failed_attempts:
                self.failed_attempts[client_ip] = 0
            self.failed_attempts[client_ip] += 1
        
        # Print real-time log with pattern analysis
        status = "SUCCESS" if success else "FAILED"
        print(f"[{timestamp}] {client_ip} - {username}:{password} - {status}{pattern_analysis}")
    
    def parse_http_request(self, request):
        """Parse HTTP POST request to extract credentials"""
        try:
            lines = request.split('\r\n')
            method_line = lines[0]
            
            if not method_line.startswith("POST /login"):
                return None, None
            
            # Find the body (after empty line)
            body_start = -1
            for i, line in enumerate(lines):
                if line == '':
                    body_start = i + 1
                    break
            
            if body_start == -1 or body_start >= len(lines):
                return None, None
            
            body = lines[body_start]
            
            # Parse form data
            params = {}
            for param in body.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[unquote_plus(key)] = unquote_plus(value)
            
            username = params.get('username', '')
            password = params.get('password', '')
            
            return username, password
            
        except Exception as e:
            print(f"[!] Error parsing request: {e}")
            return None, None
    
    def create_http_response(self, success, username=None):
        """Create HTTP response with detailed feedback"""
        if success:
            user_profile = self.users_db.get(username, {})
            personal_info = user_profile.get("personal_info", {})
            
            body = f"""
<!DOCTYPE html>
<html>
<head><title>Login Success - Known Password Attack Simulation</title></head>
<body>
    <h1>SUCCESS</h1>
    <p>Welcome {personal_info.get('full_name', username)}! Authentication successful.</p>
    <p>Login Time: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>Session ID: {hashlib.md5(str(time.time()).encode()).hexdigest()}</p>
    <hr>
    <p><em>Known Password Attack Simulation - Educational Purposes</em></p>
</body>
</html>
"""
            response = f"""HTTP/1.1 200 OK\r
Content-Type: text/html\r
Content-Length: {len(body)}\r
Connection: close\r
\r
{body}"""
        else:
            body = """
<!DOCTYPE html>
<html>
<head><title>Login Failed - Known Password Attack Simulation</title></head>
<body>
    <h1>FAILED</h1>
    <p>Invalid username or password.</p>
    <p>Please check your credentials and try again.</p>
    <hr>
    <p><em>Known Password Attack Simulation - Educational Purposes</em></p>
</body>
</html>
"""
            response = f"""HTTP/1.1 401 Unauthorized\r
Content-Type: text/html\r
Content-Length: {len(body)}\r
Connection: close\r
\r
{body}"""
        
        return response.encode()
    
    def handle_client(self, client_socket, client_address):
        """Handle individual client connection"""
        try:
            client_ip = client_address[0]
            
            # Receive request
            request = client_socket.recv(4096).decode('utf-8', errors='ignore')
            
            if not request:
                return
            
            # Parse credentials
            username, password = self.parse_http_request(request)
            
            if username is None or password is None:
                client_socket.send(self.create_http_response(False))
                return
            
            # Authenticate
            success = self.authenticate_user(username, password)
            
            # Log attempt with pattern analysis
            self.log_attempt(client_ip, username, password, success)
            
            # Send response
            response = self.create_http_response(success, username)
            client_socket.send(response)
            
        except Exception as e:
            print(f"[!] Error handling client: {e}")
        finally:
            client_socket.close()
    
    def start_server(self):
        """Start the authentication server"""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            
            self.running = True
            
            print(f"[+] Known Password Attack Server started on {self.host}:{self.port}")
            print("[*] Waiting for connections...")
            print("[*] Press Ctrl+C to stop the server\n")
            
            while self.running:
                try:
                    client_socket, client_address = server_socket.accept()
                    
                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error:
                    if self.running:
                        print("[!] Socket error occurred")
                    break
                    
        except Exception as e:
            print(f"[!] Server error: {e}")
        finally:
            server_socket.close()
            print("\n[*] Server stopped")
    
    def show_statistics(self):
        """Display detailed server statistics"""
        print("\n" + "="*70)
        print("         KNOWN PASSWORD ATTACK SERVER STATISTICS")
        print("="*70)
        
        print(f"Total authentication attempts: {len(self.attempt_log)}")
        
        successful_attempts = sum(1 for attempt in self.attempt_log if attempt['success'])
        failed_attempts = len(self.attempt_log) - successful_attempts
        
        print(f"Successful logins: {successful_attempts}")
        print(f"Failed attempts: {failed_attempts}")
        
        if self.attempt_log:
            print(f"Success rate: {(successful_attempts/len(self.attempt_log)*100):.1f}%")
        
        print("\nUser account statistics:")
        for username, data in self.users_db.items():
            print(f"  {username}:")
            print(f"    Password: {data['plain_password']} (Pattern: {data['password_pattern']})")
            print(f"    Attempts: {data['login_attempts']}, Successful: {data['successful_logins']}")
        
        if self.failed_attempts:
            print(f"\nFailed attempts by IP:")
            for ip, count in self.failed_attempts.items():
                print(f"  {ip}: {count} failed attempts")
        
        # Pattern analysis
        print(f"\nPassword Pattern Analysis:")
        pattern_attempts = [attempt for attempt in self.attempt_log if attempt['pattern_analysis']]
        if pattern_attempts:
            print(f"  Attempts using personal information: {len(pattern_attempts)}")
            for attempt in pattern_attempts[-5:]:  # Show last 5
                print(f"    {attempt['username']}:{attempt['password']}{attempt['pattern_analysis']}")
        else:
            print("  No attempts detected using personal information patterns")
        
        print(f"\nRecent attempts:")
        recent_attempts = self.attempt_log[-10:] if len(self.attempt_log) > 10 else self.attempt_log
        for attempt in recent_attempts:
            status = "SUCCESS" if attempt['success'] else "FAILED"
            print(f"  [{attempt['timestamp']}] {attempt['client_ip']} - {attempt['username']}:{attempt['password']} - {status}{attempt['pattern_analysis']}")

def main():
    print("="*70)
    print("     KNOWN PASSWORD ATTACK SIMULATION - VICTIM SERVER")
    print("="*70)
    print("Educational/Defensive Security Purposes Only")
    print("="*70)
    
    # Get server configuration (default to container network settings)
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--docker":
        host = "0.0.0.0"  # Listen on all interfaces in container
        port = 8081
        print(f"\n[*] Running in Docker mode")
        print(f"[*] Server will bind to {host}:{port}")
    else:
        host = input("\nEnter server host (default: 127.0.0.1): ").strip() or "127.0.0.1"
        port = int(input("Enter server port (default: 8081): ").strip() or "8081")
    
    # Create and start server
    server = KnownPasswordAuthServer(host, port)
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n[*] Server shutdown requested")
        server.running = False
        server.show_statistics()
    except Exception as e:
        print(f"\n[!] Server error: {e}")

if __name__ == "__main__":
    main()