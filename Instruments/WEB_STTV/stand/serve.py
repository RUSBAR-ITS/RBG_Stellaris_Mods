"""Serve this test VM's built frontend and forward its API calls on loopback."""
import http.client
import json
import shutil
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
API = json.loads((ROOT.parent / 'server/config/server.json').read_text())['http']
ROUTES = {'/api/trees/reference': {'POST', 'DELETE'}, '/api/trees/reference/dlcs': {'GET'},
          '/api/trees/research-progress': {'DELETE'}, '/api/trees/generated': {'DELETE'},
          '/api/trees/technology-tooltip': {'POST'}, '/api/trees/technology-tooltips': {'DELETE'},
          '/api/localization/lookup': {'POST'}}


class Frontend(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / 'public'), **kwargs)

    def list_directory(self, path):
        self.send_error(404)
        return None

    def do_GET(self):
        if urlsplit(self.path).path.startswith('/api/'):
            return self.proxy()
        super().do_GET()

    def proxy(self):
        path = urlsplit(self.path).path
        if self.command not in ROUTES.get(path, set()):
            return self.send_error(404)
        if self.headers.get('Transfer-Encoding'):
            return self.send_error(411)
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length < 0:
                raise ValueError()
        except ValueError:
            return self.send_error(400)
        upstream = http.client.HTTPConnection(API['host'], API['port'], timeout=120)
        try:
            data = self.rfile.read(length) if length else None
            upstream.request(self.command, self.path, body=data, headers={'Content-Type': 'application/json'})
            response = upstream.getresponse()
        except (OSError, http.client.HTTPException):
            upstream.close()
            return self.send_error(502)
        try:
            self.send_response(response.status)
            for key in ('Content-Type', 'Content-Length'):
                if key in response.headers:
                    self.send_header(key, response.headers[key])
            self.end_headers()
            shutil.copyfileobj(response, self.wfile)
        except (BrokenPipeError, ConnectionResetError):
            self.close_connection = True
        finally:
            upstream.close()

    do_POST = do_DELETE = proxy


with ThreadingHTTPServer(('0.0.0.0', 5173), Frontend) as server:
    server.serve_forever()
