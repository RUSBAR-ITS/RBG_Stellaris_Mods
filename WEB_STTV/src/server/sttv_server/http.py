"""HTTP interface for localization, reference trees and technology tooltips."""

import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from pymongo.errors import PyMongoError

from .localization import lookup
from .tree.errors import BuildError


def make_server(address, read_strings, trees=None, tooltip=None):
    class Handler(BaseHTTPRequestHandler):
        def reply(self, status, payload):
            body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            path = urlsplit(self.path).path
            tree = path == '/api/trees/reference' and trees is not None
            content = path == '/api/trees/technology-tooltip' and tooltip is not None
            if not tree and not content and path != '/api/localization/lookup':
                return self.reply(404, {'error': 'not_found'})
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if size <= 0:
                    raise ValueError('Expected a JSON body')
                body = json.loads(self.rfile.read(size).decode('utf-8'))
                if tree:
                    return self.tree_request(lambda: trees.open(body))
                if not isinstance(body, dict) or body.get('language') not in ('ru', 'en'):
                    raise ValueError('Expected a supported language')
                if content:
                    identifier = body.get('technology_id')
                    if not isinstance(identifier, str) or not identifier.strip():
                        raise ValueError('Expected a technology ID')
                    identifier.encode('utf-8')
                    return self.tooltip_request(identifier, body['language'])
                keys = body.get('keys')
                if not isinstance(keys, list) or not all(isinstance(k, str) and k for k in keys):
                    raise ValueError('Expected an array of keys')
                for key in keys:
                    key.encode('utf-8')
            except (ValueError, OverflowError, RecursionError):
                return self.reply(400, {'error': 'invalid_request'})
            try:
                result = lookup(body['language'], keys, read_strings)
            except PyMongoError:
                return self.reply(503, {'error': 'database_unavailable'})
            self.reply(200, result)

        def tooltip_request(self, identifier, language):
            try:
                result = tooltip(identifier, language)
            except PyMongoError:
                logging.exception('MongoDB tooltip lookup failed')
                return self.reply(503, {'error': 'database_unavailable'})
            except Exception:
                logging.exception('Technology tooltip failed for %r', identifier)
                return self.reply(500, {'error': 'tooltip_failed'})
            if result is None:
                return self.reply(404, {'error': 'technology_not_found'})
            self.reply(200, result)

        def tree_request(self, operation):
            try:
                result = operation()
            except BuildError as exc:
                return self.reply(exc.status, {'error': exc.code, 'reason': str(exc)})
            except PyMongoError:
                logging.exception('MongoDB tree operation failed')
                return self.reply(503, {'error': 'database_unavailable'})
            except Exception:
                logging.exception('Reference tree operation failed')
                return self.reply(500, {'error': 'tree_failed'})
            self.reply(200, result)

        def do_GET(self):
            if self.path == '/api/trees/reference/dlcs' and trees is not None:
                return self.tree_request(trees.dlcs)
            self.reply(404, {'error': 'not_found'})

        def do_DELETE(self):
            if urlsplit(self.path).path != '/api/trees/reference' or trees is None:
                return self.reply(404, {'error': 'not_found'})
            if urlsplit(self.path).query or self.headers.get('Content-Length', '0') != '0' or self.headers.get('Transfer-Encoding'):
                return self.reply(400, {'error': 'invalid_request'})
            self.tree_request(trees.clear)

    return ThreadingHTTPServer(address, Handler)
