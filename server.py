# server.py
import os
import sys
import time
import json
import atexit
import signal
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
from datetime import datetime

# Configuration
LOG_FILE = "user_interactions.log"
PORT = 8000
HOST = "0.0.0.0"
PID_FILE = "server.pid"

class PersistentRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = parse_qs(post_data.decode('utf-8'))
            
            interaction_type = data.get('type', [''])[0]
            interaction_data = json.loads(data.get('data', ['{}'])[0])
            
            self._log_interaction({
                'timestamp': datetime.now().isoformat(),
                'type': interaction_type,
                'data': interaction_data,
                'ip': self.client_address[0]
            })
            
            self._set_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "received": interaction_type
            }).encode('utf-8'))
            
        except Exception as e:
            self._log_error(f"Request error: {str(e)}")
            self._set_headers(400)
            self.wfile.write(json.dumps({
                "status": "error",
                "message": str(e)
            }).encode('utf-8'))

    def _log_interaction(self, data):
        """Append to existing log file"""
        try:
            with open(LOG_FILE, "a") as f:
                f.write(json.dumps(data) + "\n")
        except Exception as e:
            self._log_error(f"Log write failed: {str(e)}")

    def _log_error(self, message):
        """Log errors separately"""
        with open("errors.log", "a") as f:
            f.write(f"{datetime.now().isoformat()} - {message}\n")

class AutoStartServer:
    def __init__(self):
        self.server = None
        self._cleanup_old_pid()
        
    def _cleanup_old_pid(self):
        """Remove stale PID file if exists"""
        if os.path.exists(PID_FILE):
            try:
                with open(PID_FILE, "r") as f:
                    pid = int(f.read().strip())
                    try:
                        os.kill(pid, 0)  # Check if process exists
                    except OSError:
                        os.remove(PID_FILE)  # Process doesn't exist
            except:
                try:
                    os.remove(PID_FILE)
                except:
                    pass

    def start(self, daemon=False):
        """Start server with auto-recovery"""
        if daemon:
            self._daemonize()
            
        # Write PID file
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))
        
        # Register cleanup
        atexit.register(self._cleanup)
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
        
        # Start server
        self.server = HTTPServer((HOST, PORT), PersistentRequestHandler)
        print(f"Server running at http://{HOST}:{PORT}")
        print(f"Logging to: {LOG_FILE} (appending to existing file)")
        self.server.serve_forever()

    def _daemonize(self):
        """Background the server process"""
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write(f"Fork failed: {e}\n")
            sys.exit(1)
            
        os.setsid()
        os.umask(0)
        sys.stdout.flush()
        sys.stderr.flush()
        
        # Redirect standard file descriptors
        with open(os.devnull, 'rb') as f:
            os.dup2(f.fileno(), sys.stdin.fileno())
        with open(os.devnull, 'ab') as f:
            os.dup2(f.fileno(), sys.stdout.fileno())
            os.dup2(f.fileno(), sys.stderr.fileno())

    def _handle_signal(self, signum, frame):
        """Handle termination signals"""
        self._cleanup()
        if self.server:
            self.server.shutdown()
        sys.exit(0)

    def _cleanup(self):
        """Cleanup on exit"""
        if os.path.exists(PID_FILE):
            try:
                os.remove(PID_FILE)
            except:
                pass

def check_and_start_server():
    """Check if server is running, start if not"""
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
                try:
                    os.kill(pid, 0)  # Check if process exists
                    print(f"Server already running with PID {pid}")
                    return True
                except OSError:
                    pass  # Process doesn't exist
        except:
            pass
    
    # Initialize log file if doesn't exist
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write("")  # Create empty file
    
    # Start server
    server = AutoStartServer()
    server.start(daemon=True)
    return True

if __name__ == "__main__":
    # Check for daemon mode
    daemon_mode = "--daemon" in sys.argv or "-d" in sys.argv
    
    if "--check" in sys.argv:
        check_and_start_server()
    else:
        # Initialize log file if doesn't exist
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w") as f:
                f.write("")  # Create empty file
        
        # Start server
        server = AutoStartServer()
        server.start(daemon=daemon_mode)