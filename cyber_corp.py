# cyber_corp.py
import random
from datetime import datetime
import json
import hashlib
import logging
from pathlib import Path
import threading
from urllib.request import Request
import webbrowser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cyber_corp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CyberCorp")

# Game configuration - renamed properties
CONFIG = {
    "develop_cost": 200,          # was research_cost
    "develop_min_progress": 5,     # was research_min_gain
    "develop_max_progress": 15,    # was research_max_gain
    "influence_cost": 300,         # was bribe_cost
    "influence_min_reduction": 10, # was bribe_min_reduction
    "influence_max_reduction": 20, # was bribe_max_reduction
    "firewall_cost": 400,          # was security_cost
    "firewall_min_boost": 10,      # was security_min_gain
    "firewall_max_boost": 25,      # was security_max_gain
    "sell_tech_min": 500,          # was sell_min_gain
    "sell_tech_max": 1300,         # was sell_max_gain
    "sell_attention_gain": 15,     # was sell_suspicion_gain
    "monthly_costs_min": 50,       # was monthly_expenses_min
    "monthly_costs_max": 150       # was monthly_expenses_max
}

# In-memory storage
active_operations = {}  # was active_games
corp_directors = {}     # was player_data

class CyberState:
    def __init__(self):
        self.budget = 1000         # was money
        self.progress = 0           # was research
        self.firewall = 50          # was security
        self.attention = 0          # was suspicion
        self.quarter = 1            # was month
        self.terminated = False     # was game_over
        self.termination_reason = None  # was game_over_reason
        self.operation_log = []     # was last_events

class DirectorProfile:
    def __init__(self, director_id, alias=None):
        self.director_id = director_id
        self.alias = alias or "Ghost"
        self.peak_quarters = 0      # was high_score
        self.missions = 0           # was games_played
        self.milestones = {         # was achievements
            "first_success": False,
            "bankrupt": False,
            "system_breach": False,
            "government_raid": False
        }

# Helper functions
def generate_director_id(alias=None):
    """Generate unique ID using quantum encryption simulation"""
    timestamp = str(datetime.now().timestamp()).encode()
    alias_bytes = alias.encode() if alias else b''
    return hashlib.sha3_256(timestamp + alias_bytes).hexdigest()[:16]

def save_corp_data():
    data = {
        "directors": {k: v.__dict__ for k, v in corp_directors.items()},
        "config": CONFIG
    }
    with open('corp_data.enc', 'w') as f:
        json.dump(data, f)

def load_corp_data():
    try:
        if Path('corp_data.enc').exists():
            with open('corp_data.enc', 'r') as f:
                data = json.load(f)
                for director_id, profile in data.get("directors", {}).items():
                    corp_directors[director_id] = DirectorProfile("")
                    corp_directors[director_id].__dict__.update(profile)
                CONFIG.update(data.get("config", CONFIG))
    except Exception as e:
        logger.error(f"Data decryption failed: {e}")

# Event system - cyber-themed
def quantum_breakthrough():
    return {
        "progress": random.randint(5, 15),
        "message": "Quantum algorithm breakthrough! Progress +{progress}%",
        "type": "positive"
    }

def darknet_infiltration():
    return {
        "firewall_loss": random.randint(10, 30),
        "message": "Darknet operatives breached sector! Firewall -{firewall_loss}%",
        "type": "critical"
    }

def random_cyber_event(state):
    events = [
        {
            "name": "Darknet Infiltration",
            "chance": min(0.1 + (state.attention / 200), 0.5),
            "effect": darknet_infiltration
        },
        {
            "name": "Whistleblower",
            "chance": min(0.05 + (state.attention / 150), 0.4),
            "effect": lambda: {
                "attention_gain": random.randint(10, 25),
                "message": "Internal leak detected! Attention +{attention_gain}%",
                "type": "warning"
            }
        },
        {
            "name": "AI Breakthrough",
            "chance": 0.1,
            "effect": quantum_breakthrough
        }
    ]
    
    return [e["effect"]() for e in events if random.random() < e["chance"]]

def check_termination(state):
    if state.firewall <= 0:
        return "system_breach"
    if state.attention >= 100:
        return "government_raid"
    if state.progress >= 100:
        return "success"
    if state.budget <= 0:
        return "bankruptcy"
    return None

# Game operations
def initiate_operation(alias=None):
    director_id = generate_director_id(alias)
    
    if director_id not in corp_directors:
        corp_directors[director_id] = DirectorProfile(director_id, alias)
    
    operation = CyberState()
    active_operations[director_id] = operation
    
    logger.info(f"New operation initiated by Director {director_id}")
    return {
        "director_id": director_id,
        "operation_state": operation.__dict__,
        "message": "Cyber division activated"
    }

def execute_directive(director_id, directive):
    if director_id not in active_operations:
        raise ValueError("Operation not found")
    
    op = active_operations[director_id]
    if op.terminated:
        raise ValueError("Operation terminated")
    
    response = {"message": "", "events": []}
    
    try:
        if directive == "develop":
            if op.budget >= CONFIG["develop_cost"]:
                op.budget -= CONFIG["develop_cost"]
                progress = random.randint(
                    CONFIG["develop_min_progress"],
                    CONFIG["develop_max_progress"]
                )
                op.progress = min(op.progress + progress, 100)
                response["message"] = f"R&D completed. Progress +{progress}%"
                
                if random.random() < 0.3 and op.progress > 20:
                    breach = random.randint(5, 20)
                    op.firewall = max(0, op.firewall - breach)
                    response["events"].append({
                        "message": f"Security lapse detected! Firewall -{breach}%",
                        "type": "warning"
                    })
        
        # Other directives would be implemented similarly...
        
        # Check termination
        if reason := check_termination(op):
            op.terminated = True
            op.termination_reason = reason
            
            director = corp_directors.get(director_id)
            if director:
                director.missions += 1
                if reason == "success":
                    director.peak_quarters = max(director.peak_quarters, op.quarter)
                    director.milestones["first_success"] = True
        
        return {
            "director_id": director_id,
            "operation_state": op.__dict__,
            **response
        }
    
    except Exception as e:
        logger.error(f"Directive failed: {e}")
        raise

# Main execution
if __name__ == "__main__":
    load_corp_data()
    
    # Example usage:
    new_op = initiate_operation("Neo")
    print(f"New operation ID: {new_op['director_id']}")
    
    try:
        result = execute_directive(new_op['director_id'], "develop")
        print(f"Operation state: {result['operation_state']}")
    except Exception as e:
        print(f"Error: {e}")
    
    save_corp_data()
if __name__ == "__main__":
    from concurrent.futures import ThreadPoolExecutor
    import socket
    from functools import partial

    # Custom ASGI server implementation
    class SimpleASGIServer:
        def __init__(self, app, host='0.0.0.0', port=8000):
            self.app = app
            self.host = host
            self.port = port
            self.executor = ThreadPoolExecutor(max_workers=10)

        async def handle_connection(self, reader, writer):
            try:
                # Parse HTTP request
                request = await reader.read(4096)
                headers, body = request.split(b'\r\n\r\n', 1) if b'\r\n\r\n' in request else (request, b'')
                
                # Convert to ASGI scope
                scope = {
                    'type': 'http',
                    'method': headers.split(b' ')[0].decode(),
                    'path': headers.split(b' ')[1].decode(),
                    'headers': [],
                    'body': body
                }

                # Create ASGI message handler
                async def receive():
                    return {'body': body, 'more_body': False}

                async def send(message):
                    if message['type'] == 'http.response.start':
                        writer.write(
                            f"HTTP/1.1 {message['status']}\r\n".encode() +
                            b"\r\n".join(
                                f"{k}: {v}".encode() for k, v in message['headers']
                            ) + b"\r\n\r\n"
                        )
                    else:
                        writer.write(message['body'])
                    await writer.drain()

                # Dispatch to FastAPI
                await self.app(scope, receive, send)

            except Exception as e:
                print(f"Connection error: {e}")
            finally:
                writer.close()

        async def run(self):
            server = await asyncio.start_server(
                self.handle_connection,
                self.host,
                self.port
            )
            print(f"Server running on {self.host}:{self.port}")
            await server.serve_forever()

    try:
        import asyncio
        server = SimpleASGIServer(app) # type: ignore
        
        # Start web server in background
        web_thread = threading.Thread(target=run_web_server, daemon=True) # type: ignore
        web_thread.start()
        
        # Open browser
        webbrowser.open("http://localhost:8000/game.html")
        
        # Run ASGI server
        asyncio.run(server.run())
        
    except Exception as e:
        with open('error.log', 'a') as f:
            f.write(f"{datetime.now()} - ERROR: {str(e)}\n")
        print("Server crashed! See error.log for details")

# Add to your imports
import logging
from datetime import datetime

# Configure logging (add this right after your imports)
logging.basicConfig(
    filename='cybercorp_actions.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Example of logging a user action (add inside your endpoint functions)
@app.post("/develop") # type: ignore
async def develop_tech(director_id: str):
    logging.info(f"Director {director_id} performed DEVELOP action")
    # ... rest of your function code
@app.middleware("http") # type: ignore
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    logging.info(f"{request.method} {request.url.path} - {response.status_code}")
    return response


