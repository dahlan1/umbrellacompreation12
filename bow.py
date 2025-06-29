import http.server
import socketserver
import os
import json
from urllib.parse import urlparse, parse_qs

# Configuration
PORT = 8000
HTML_FILE = "bow.html"  # Your HTML file name
DATA_FILE = "bows.json"  # File to store B.O.W data if needed

class UmbrellaRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Handle language change requests
        if self.path.startswith('/change_language'):
            query = urlparse(self.path).query
            params = parse_qs(query)
            lang = params.get('lang', ['en'])[0]
            
            # In a real app, you might save this to a session or database
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'success', 'language': lang}).encode())
            return
            
        # Serve the main HTML file for all other GET requests
        if self.path == '/' or self.path == '/bow.html':
            self.path = HTML_FILE
            
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        # Handle form submissions or other POST requests
        if self.path == '/save_bow':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            # Here you would typically save to a database
            # For this example, we'll just save to a JSON file
            try:
                with open(DATA_FILE, 'w') as f:
                    json.dump(data, f)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success'}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode())
            return
            
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'404 Not Found')
def do_GET(self):
    if self.path.startswith('/change_language'):
        query = urlparse(self.path).query
        params = parse_qs(query)
        lang = params.get('lang', ['en'])[0]
        
        # Here you would typically save to user session/database
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'success', 
            'language': lang,
            'message': f'Language changed to {lang}'
        }).encode())
        return
        
    # ... rest of your GET handling

def do_POST(self):
    if self.path == '/save_bow':
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode())
            # Here you would save to database
            # For now just log and return success
            print("Received B.O.W data:", data)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'success',
                'received_data': data
            }).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'error',
                'message': str(e)
            }).encode())
        return
    
    # ... rest of your POST handling

def main():
    # Change working directory to the directory containing this script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Create the handler
    handler = UmbrellaRequestHandler
    
    # Start the server
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        print(f"Main page: http://localhost:{PORT}/{HTML_FILE}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")

if __name__ == "__main__":
    main()
    