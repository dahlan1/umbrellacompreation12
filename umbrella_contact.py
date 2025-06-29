import http.server
import socketserver
import json
from urllib.parse import parse_qs, urlparse
import mimetypes
import os
import threading
import webbrowser
from datetime import datetime

PORT = 8000
SUBMISSIONS_FILE = "umbrella_submissions.txt"

class UmbrellaRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL path
        parsed_path = urlparse(self.path)
        
        # Serve the HTML file for root path
        if parsed_path.path == '/':
            self.path = 'umbrella_contact.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        # Handle other static files (CSS, JS, images)
        if os.path.exists(parsed_path.path[1:]):
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        # Handle API requests
        if parsed_path.path == '/api/contact':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "success",
                "message": "Your message has been received. A representative will contact you shortly."
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        
        # 404 for other paths
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'404 Not Found')

    def do_POST(self):
        # Only handle contact form submissions
        if self.path == '/api/contact':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                # Parse form data
                data = parse_qs(post_data)
                
                # Prepare data for saving
                submission = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "name": data.get('name', [''])[0],
                    "email": data.get('email', [''])[0],
                    "department": data.get('department', [''])[0],
                    "subject": data.get('subject', [''])[0],
                    "message": data.get('message', [''])[0]
                }
                
                # Save to text file
                self.save_submission(submission)
                
                # Print to console for monitoring
                print(f"New submission received at {submission['timestamp']}:")
                print(f"From: {submission['name']} <{submission['email']}>")
                print(f"Department: {submission['department']}")
                print(f"Subject: {submission['subject']}")
                print("-" * 40)
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "status": "success",
                    "message": "Your message has been received. A representative will contact you shortly."
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                # Log error
                print(f"Error processing submission: {str(e)}")
                
                # Send error response
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "status": "error",
                    "message": "An error occurred while processing your request."
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        
        # 404 for other POST paths
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'404 Not Found')

    def save_submission(self, submission):
        """Save submission data to text file with proper formatting"""
        with open(SUBMISSIONS_FILE, "a", encoding="utf-8") as f:
            f.write(f"=== New Submission ===\n")
            f.write(f"Timestamp: {submission['timestamp']}\n")
            f.write(f"Name: {submission['name']}\n")
            f.write(f"Email: {submission['email']}\n")
            f.write(f"Department: {submission['department']}\n")
            f.write(f"Subject: {submission['subject']}\n")
            f.write(f"Message:\n{submission['message']}\n")
            f.write("=" * 30 + "\n\n")

def run_server():
    # Create submissions file if it doesn't exist
    if not os.path.exists(SUBMISSIONS_FILE):
        with open(SUBMISSIONS_FILE, "w", encoding="utf-8") as f:
            f.write("Umbrella Corporation Contact Form Submissions\n")
            f.write(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
    
    # Set up MIME types
    mimetypes.init()
    mimetypes.add_type('application/javascript', '.js')
    
    # Start the server
    handler = UmbrellaRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Umbrella Corporation contact form server running at port {PORT}")
        print(f"Access the contact page at: http://localhost:{PORT}/")
        print(f"All submissions are being saved to: {SUBMISSIONS_FILE}")
        print("Press Ctrl+C to stop the server\n")
        
        # Open browser automatically
        threading.Thread(target=lambda: webbrowser.open(f'http://localhost:{PORT}')).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer is shutting down...")
            httpd.shutdown()

if __name__ == "__main__":
    run_server()