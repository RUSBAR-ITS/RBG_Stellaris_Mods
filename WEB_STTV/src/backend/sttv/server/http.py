"""Read-only localization endpoint with an explicitly configured URL prefix."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit

from pymongo.errors import PyMongoError


def lookup(collection, language, key):
    return collection.find_one({'_id': {'language': language, 'key': key}})


def make_server(collection, http):
    prefix = http['prefix'].strip('/').split('/')

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parts = urlsplit(self.path).path.strip('/').split('/')
            if parts[:-2] != prefix or len(parts) != len(prefix) + 2:
                return self.send_error(404)
            try:
                document = lookup(collection, *map(unquote, parts[-2:]))
            except PyMongoError:
                return self.send_error(503)
            if document is None:
                return self.send_error(404)
            body = json.dumps(document, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return ThreadingHTTPServer((http['host'], http['port']), Handler)
