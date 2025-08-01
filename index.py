
from http.server import BaseHTTPRequestHandler, HTTPServer
from baseIndex import runConnectorFull


class Handler(BaseHTTPRequestHandler):
 
  def do_GET(self):
    
     try:
      runConnectorFull() 
      print("indexing function is called ✅")
       
      self.send_response(200)
      self.send_header("Content-type", "text/plain")
      self.end_headers()
      self.wfile.write(b"Glean indexing completed successfully")
  
      print("periodical indexing successfully invoked ✅")
      return {
        "status-code" : 200,
        "body": "Glean indexing completed successfully"
       }
      
     except Exception as error:
      print("invokation failed ❌", error)
    
    
if __name__ == "__main__":
  host = "0.0.0.0"
  port = 8000  ## change port number in production
  server = HTTPServer((host, port), Handler)
  print(f"running on {host} : {port}")
  server.serve_forever()
  
  
  