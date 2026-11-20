"""JSON transport and immutable, declared-file reads; no arbitrary paths or commands."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import shutil
from urllib.parse import urlsplit

from sttv.common.errors import BuildError
from sttv.storage.settings import confined


def create_server(options, operations):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_GET(self):
            self.dispatch()

        def do_POST(self):
            self.dispatch()

        def dispatch(self):
            try:
                origin = self.headers.get('Origin')
                if origin and origin not in options['allowed_origins']:
                    raise BuildError('invalid_origin', 'Origin is not allowed')
                path = urlsplit(self.path).path
                prefix = options['prefix'] + '/'
                if not path.startswith(prefix):
                    raise BuildError('unknown_route', 'Unknown API route')
                parts = path[len(prefix):].split('/')
                token = self.headers.get('X-Sttv-Session', '')
                payload = self.payload() if self.command == 'POST' else {}
                if parts == ['connect'] and self.command == 'POST':
                    return self.send_json(operations.connect(payload))
                if parts == ['operations'] and self.command == 'POST':
                    return self.send_json(operations.start(token, payload))
                if len(parts) in (2, 3) and parts[0] == 'operations':
                    if len(parts) == 2 and self.command == 'GET':
                        return self.send_json(operations.get(token, parts[1]))
                    if parts[2:] == ['cancel'] and self.command == 'POST':
                        return self.send_json(operations.get(token, parts[1], cancel=True))
                if len(parts) >= 3 and parts[0] == 'snapshots' and self.command == 'GET':
                    manifest = operations.snapshot(token, parts[1])
                    if parts[2:] == ['manifest']:
                        return self.send_json(manifest)
                    row = None
                    if len(parts) == 5 and parts[2] == 'documents':
                        row = next((d for d in manifest['datasets'].get(parts[3], {}).get('documents', [])
                                    if d['document_id'] == parts[4]), None)
                    if len(parts) == 4 and parts[2] == 'images':
                        row = manifest.get('presentation', {}).get('files', {}).get(parts[3])
                    if row:
                        return self.send_file(row)
                raise BuildError('unknown_route', 'Unknown API route or undeclared resource')
            except (BuildError, ValueError, TypeError, KeyError) as exc:
                self.send_json({'error': {'code': getattr(exc, 'code', 'invalid_request'), 'message': str(exc)}}, 400)
            except OSError as exc:
                if not isinstance(exc, (BrokenPipeError, ConnectionResetError, ConnectionAbortedError)):
                    self.send_json({'error': {'code': 'service_io', 'message': str(exc)}}, 500)

        def payload(self):
            length = int(self.headers.get('Content-Length', '0'))
            if length <= 0 or length > options['max_request_bytes']:
                raise BuildError('request_size', 'Invalid request size')
            value = json.loads(self.rfile.read(length))
            if not isinstance(value, dict):
                raise BuildError('invalid_request', 'Expected a JSON object')
            return value

        def send_json(self, value, status=200):
            payload = json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def send_file(self, row):
            path = confined(operations.settings.storage.root, row['path'])
            with path.open('rb') as handle:
                self.send_response(200)
                self.send_header('Content-Type', row.get('mime_type', 'application/json'))
                self.send_header('Content-Length', str(path.stat().st_size))
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                shutil.copyfileobj(handle, self.wfile)

    return ThreadingHTTPServer((options['host'], options['port']), Handler)
