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
        """Initialize user database with realistic personal information-based passwords"""
        # Realistic user profiles with personal information
        user_profiles = {
            "john.smith": {
                "personal_info": {
                    "full_name": "John Smith",
                    "birth_year": "1985",
                    "birth_date": "15031985",  # 15th March 1985
                    "pet_name": "Buddy",
                    "hometown": "Boston",
                    "favorite_team": "Patriots",
                    "company": "TechCorp"
                },
                "password": "John1985!",  # Name + birth year + special char
                "password_pattern": "FirstName + BirthYear + Special"
            },
            "sarah.jones": {
                "personal_info": {
                    "full_name": "Sarah Jones", 
                    "birth_year": "1992",
                    "birth_date": "22081992",  # 22nd August 1992
                    "pet_name": "Luna",
                    "hometown": "Seattle",
                    "favorite_team": "Seahawks",
                    "company": "DataSoft"
                },
                "password": "Luna2024",  # Pet name + current year
                "password_pattern": "PetName + CurrentYear"
            },
            "mike.johnson": {
                "personal_info": {
                    "full_name": "Michael Johnson",
                    "birth_year": "1978",
                    "birth_date": "10121978",  # 10th December 1978
                    "pet_name": "Max",
                    "hometown": "Chicago", 
                    "favorite_team": "Bears",
                    "company": "InfoTech"
                },
                "password": "Chicago78!",  # Hometown + birth year + special
                "password_pattern": "Hometown + BirthYear + Special"
            },
            "anna.wilson": {
                "personal_info": {
                    "full_name": "Anna Wilson",
                    "birth_year": "1990",
                    "birth_date": "05071990",  # 5th July 1990
                    "pet_name": "Bella",
                    "hometown": "Denver",
                    "favorite_team": "Broncos",
                    "company": "CloudTech"
                },
                "password": "Bella@90",  # Pet + birth year suffix
                "password_pattern": "PetName + BirthYear(suffix) + Special"
            },
            "david.brown": {
                "personal_info": {
                    "full_name": "David Brown",
                    "birth_year": "1983",
                    "birth_date": "18111983",  # 18th November 1983
                    "pet_name": "Rocky",
                    "hometown": "Miami",
                    "favorite_team": "Dolphins",
                    "company": "SecureTech"
                },
                "password": "Dolphins83",  # Favorite team + birth year
                "password_pattern": "FavoriteTeam + BirthYear"
            }
        }
        
        for username, profile in user_profiles.items():
            password = profile["password"]
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            self.users_db[username] = {
                "password_hash": password_hash,
                "plain_password": password,  # For simulation purposes only
                "personal_info": profile["personal_info"],
                "password_pattern": profile["password_pattern"],
                "login_attempts": 0,
                "successful_logins": 0
            }
        
        print(f"[*] Initialized {len(self.users_db)} user profiles for known password attack")
        print("[*] User profiles and password patterns:")
        for username, data in self.users_db.items():
            print(f"    {username}:")
            print(f"      Password: {data['plain_password']}")
            print(f"      Pattern: {data['password_pattern']}")
            print(f"      Personal Info: {data['personal_info']['full_name']}, Born: {data['personal_info']['birth_year']}")
            print(f"      Pet: {data['personal_info']['pet_name']}, Hometown: {data['personal_info']['hometown']}")
            print()
    
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