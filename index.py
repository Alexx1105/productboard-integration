
from http.server import BaseHTTPRequestHandler
from baseIndex import runConnector


class handler(BaseHTTPRequestHandler):
  
 try:
  def do_GET(self):
    runConnector()
    
    self.send_response(200)
    self.send_header("Content-type", "text/plain")
    self.end_headers()
    self.wfile.write(b"Glean indexing completed successfully")
    
    return {
        "status-code" : 200,
        "body": "Glean indexing completed successfully"
    }
  
    print("periodical indexing successfully invoked ✅")
 except Exception as error:
    print("invokation failed ❌", error)
    
    