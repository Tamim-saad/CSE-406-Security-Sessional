#!/usr/bin/env python3

import socket
import threading
import hashlib
import time
import json
from urllib.parse import unquote_plus

class AuthServer:
    def __init__(self, host="127.0.0.1", port=8080):
        self.host = host
        self.port = port
        self.users_db = {}
        self.attempt_log = []
        self.failed_attempts = {}
        self.running = False
        
        # Initialize default users with hashed passwords
        self.initialize_users()
        
    def initialize_users(self):
        """Initialize user database with hashed passwords"""
        # Default users for simulation
        users = {
            "admin": "secret",
            "user": "password123", 
            "test": "test123",
            "root": "toor",
            "guest": "guest"
        }
        
        for username, password in users.items():
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            self.users_db[username] = {
                "password_hash": password_hash,
                "plain_password": password,  # For simulation purposes only
                "login_attempts": 0,
                "successful_logins": 0
            }
        
        print(f"[*] Initialized {len(self.users_db)} users in database")
        print("[*] Default credentials:")
        for username, data in self.users_db.items():
            print(f"    {username}:{data['plain_password']}")
    
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
        """Log authentication attempt"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        attempt = {
            "timestamp": timestamp,
            "client_ip": client_ip,
            "username": username,
            "password": password,
            "success": success
        }
        
        self.attempt_log.append(attempt)
        
        # Track failed attempts per IP
        if not success:
            if client_ip not in self.failed_attempts:
                self.failed_attempts[client_ip] = 0
            self.failed_attempts[client_ip] += 1
        
        # Print real-time log
        status = "SUCCESS" if success else "FAILED"
        print(f"[{timestamp}] {client_ip} - {username}:{password} - {status}")
    
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
        """Create HTTP response"""
        if success:
            body = f"""
<!DOCTYPE html>
<html>
<head><title>Login Success</title></head>
<body>
    <h1>SUCCESS</h1>
    <p>Welcome {username}! Authentication successful.</p>
    <p>Session ID: {hashlib.md5(str(time.time()).encode()).hexdigest()}</p>
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
<head><title>Login Failed</title></head>
<body>
    <h1>FAILED</h1>
    <p>Invalid username or password.</p>
    <p>Please try again.</p>
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
            
            # Log attempt
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
            
            print(f"[+] Authentication server started on {self.host}:{self.port}")
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
        """Display server statistics"""
        print("\n" + "="*60)
        print("            AUTHENTICATION SERVER STATISTICS")
        print("="*60)
        
        print(f"Total authentication attempts: {len(self.attempt_log)}")
        
        successful_attempts = sum(1 for attempt in self.attempt_log if attempt['success'])
        failed_attempts = len(self.attempt_log) - successful_attempts
        
        print(f"Successful logins: {successful_attempts}")
        print(f"Failed attempts: {failed_attempts}")
        
        if self.attempt_log:
            print(f"Success rate: {(successful_attempts/len(self.attempt_log)*100):.1f}%")
        
        print("\nUser account statistics:")
        for username, data in self.users_db.items():
            print(f"  {username}: {data['login_attempts']} attempts, {data['successful_logins']} successful")
        
        if self.failed_attempts:
            print("\nFailed attempts by IP:")
            for ip, count in self.failed_attempts.items():
                print(f"  {ip}: {count} failed attempts")
        
        print("\nRecent attempts:")
        recent_attempts = self.attempt_log[-10:] if len(self.attempt_log) > 10 else self.attempt_log
        for attempt in recent_attempts:
            status = "SUCCESS" if attempt['success'] else "FAILED"
            print(f"  [{attempt['timestamp']}] {attempt['client_ip']} - {attempt['username']}:{attempt['password']} - {status}")

def main():
    print("="*60)
    print("      DICTIONARY ATTACK SIMULATION - VICTIM SERVER")
    print("="*60)
    print("Educational/Defensive Security Purposes Only")
    print("="*60)
    
    # Get server configuration (default to container network settings)
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--docker":
        host = "0.0.0.0"  # Listen on all interfaces in container
        port = 8080
        print(f"\n[*] Running in Docker mode")
        print(f"[*] Server will bind to {host}:{port}")
    else:
        host = input("\nEnter server host (default: 127.0.0.1): ").strip() or "127.0.0.1"
        port = int(input("Enter server port (default: 8080): ").strip() or "8080")
    
    # Create and start server
    server = AuthServer(host, port)
    
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