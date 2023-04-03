import logging
import openai
import os
import json
import base64
import io
import cgi

from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
from urllib.parse import urlparse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

openai.api_key = os.environ['OPENAI_API_KEY']

class handler(BaseHTTPRequestHandler):
    def transcribe(self, file):
        return openai.Audio.transcribe(model="whisper-1", file=file)

    
    def do_POST(self):
        content_type, _ = cgi.parse_header(self.headers.get('content-type'))
        
        if content_type == 'multipart/form-data':
            # Parse multipart form data fields
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            
            file_field = form.getfirst('file')
            with open('/tmp/speech.mp3', 'wb') as f:
                f.write(file_field)    

            with open('/tmp/speech.mp3', 'rb') as f:
                response = self.transcribe(file=f)
                # Send response
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            # Unsupported content type
            self.send_response(HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
            self.end_headers()
            self.wfile.write(b'Unsupported media type')
        return    
    