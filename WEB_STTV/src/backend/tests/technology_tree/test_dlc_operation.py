"""DLC profiles publish independent combinations without changing source AST."""

from threading import Event
from unittest.mock import patch

from sttv.common.json_io import read_json
from sttv.enrichment.technology_tree.settings import load
from sttv.service.operations import Operations
from sttv.storage import open_set
from storage.fixtures import publish
from .support import SetFixture, tech, assignment as a, block as b


class DlcOperationTests(SetFixture):
    def setUp(self):
        super().setUp()
        publish(self.variables, {'dlcs': [{'source': {'root': 'STELLARIS_ROOT', 'file': 'dlc_metadata/dlc_info.txt'},
            'items': [a('dlcs', b(a('dlc001', b(a('name', 'Example')))))], 'metadata': {'expansions': []}}]})
        self.db['documents'][0]['items'] = [
            tech('parent', extra=[a('potential', b(a('host_has_dlc', 'Example')))]),
            tech('child', ['parent']), tech('zero', extra=[a('weight', '0')])]
        self.save_db()

    def test_profiles_reuse_and_orphan_keep_source(self):
        before = read_json(self.manifest)
        full = self.run_operation(dlc_enabled=None)
        self.assert_success(full)
        off = self.run_operation(dlc_enabled=[])
        self.assert_success(off)
        self.assertEqual((full['counts']['visible'], off['counts']['visible']), (3, 2))
        self.assertNotEqual(full['combination']['id'], off['combination']['id'])
        self.assertEqual(before['set_id'], read_json(self.manifest)['set_id'])
        self.assertEqual(before['datasets']['technologies']['source_revision'],
                         read_json(self.manifest)['datasets']['technologies']['source_revision'])
        rows = {n['key']['text']: n['enrichments']['technology_tree'][off['combination']['id']]
                for n in self.read_db()['documents'][0]['items']}
        self.assertFalse(rows['parent']['visibility']['visible'])
        self.assertIsNone(rows['child']['parent_tech'])
        self.assertTrue(any(n['code'] == 'no_visible_parent' for n in off['diagnostics']))
        reused = self.run_operation(dlc_enabled=['dlc001'])
        self.assert_success(reused)
        self.assertEqual(reused['action'], 'reused')
        self.assertFalse(reused['database_written'])

    def test_cancel_stale_and_unknown_profile_do_not_publish(self):
        before = self.manifest.read_bytes()
        for args, code in (({'cancelled': lambda: True, 'dlc_enabled': None}, 'cancelled'),
                           ({'expected_revision': '0' * 64}, 'stale_snapshot'),
                           ({'dlc_enabled': ['absent']}, 'unknown_dlc')):
            result = self.run_operation(**args)
            self.assertEqual(result['status'], 'failed')
            self.assertEqual(result['error']['code'], code)
            self.assertEqual(before, self.manifest.read_bytes())

    def test_service_identifies_set_serializes_jobs_and_cancels(self):
        self.assert_success(self.run_operation())
        options = {'history_limit': 16}
        service = Operations(options, self.variables, self.config, load(self.variables, self.config))
        self.addCleanup(service.close)
        manifest = read_json(self.manifest)
        connection = {'setId': manifest['set_id'], 'snapshotRevision': manifest['snapshot_revision']}
        with self.assertRaisesRegex(Exception, 'does not match'):
            service.connect({**connection, 'setId': '0' * 64})
        token = service.connect(connection)['token']
        payload = {'requestId': 'one', 'snapshotRevision': manifest['snapshot_revision'],
                   'enabled': [], 'baseCombinationId': 'reference_default'}
        entered, release, finished = Event(), Event(), Event()
        def controlled(*args, **kwargs):
            entered.set()
            release.wait(5)
            self.assertTrue(kwargs['cancelled']())
            finished.set()
            return {'status': 'failed', 'error': {'code': 'cancelled', 'message': 'Cancelled'}}
        with patch('sttv.service.operations.execute', side_effect=controlled), patch('sttv.service.operations.save_json'):
            job = service.start(token, payload)
            self.assertTrue(entered.wait(5))
            with self.assertRaisesRegex(Exception, 'Another calculation'):
                service.start(token, payload)
            service.get(token, job['id'], cancel=True)
            release.set()
            self.assertTrue(finished.wait(5))
            service.executor.shutdown(wait=True)
        self.assertEqual(service.get(token, job['id'])['status'], 'cancelled')
        self.assertEqual(read_json(self.manifest)['snapshot_revision'], manifest['snapshot_revision'])
        with self.assertRaisesRegex(Exception, 'changed'):
            service.start(token, {**payload, 'snapshotRevision': '0' * 64})

    def test_http_only_serves_declared_files_for_registered_sessions(self):
        import http.client
        import json
        from threading import Thread
        from sttv.service.http import create_server
        options = {'history_limit': 16, 'host': '127.0.0.1', 'port': 0, 'prefix': '/api/sttv',
                   'allowed_origins': ['http://127.0.0.1:5173'], 'max_request_bytes': 1024}
        service = Operations(options, self.variables, self.config, load(self.variables, self.config))
        self.addCleanup(service.close)
        server = create_server(options, service)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(lambda: (server.shutdown(), server.server_close(), thread.join()))
        manifest = read_json(self.manifest)
        token = service.connect({'setId': manifest['set_id'], 'snapshotRevision': manifest['snapshot_revision']})['token']
        client = http.client.HTTPConnection(*server.server_address, timeout=5)
        self.addCleanup(client.close)
        base = '/api/sttv/snapshots/' + manifest['snapshot_revision']
        client.request('GET', base + '/manifest', headers={'X-Sttv-Session': token})
        response = client.getresponse()
        self.assertEqual(response.status, 200)
        self.assertEqual(json.loads(response.read())['set_id'], manifest['set_id'])
        for suffix, headers in (('/documents/technologies/unknown', {'X-Sttv-Session': token}),
                                ('/manifest', {}), ('/manifest', {'Origin': 'http://unrelated.example'})):
            client.request('GET', base + suffix, headers=headers)
            response = client.getresponse()
            self.assertEqual(response.status, 400)
            self.assertIn('error', json.loads(response.read()))
        reader = open_set(self.manifest)
        identifier = reader.document_ids('technologies')[0]
        client.request('GET', base + '/documents/technologies/' + identifier, headers={'X-Sttv-Session': token})
        response = client.getresponse()
        self.assertEqual(response.status, 200)
        self.assertEqual(response.read(), reader.paths[('technologies', identifier)].read_bytes())
