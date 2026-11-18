import test from 'node:test';
import assert from 'node:assert/strict';
import { SttvOpeningController, type SttvWorkerPort } from '../../src/frontend/workers/controller';
import { sttvDiagnostic } from '../../src/frontend/workers/diagnostics';
import { sttvBuildReport } from '../../src/frontend/app/report';
import { sttvAdaptSet } from './setHarness';
import type { SttvWorkerMessage, SttvOpenCommand } from '../../src/frontend/workers/protocol';
import { sttvDatabase, sttvTechnology, sttvSet, sttvSetFiles } from './fixtures';

class SttvFakeWorker {
  onmessage: ((event: MessageEvent<SttvWorkerMessage>) => void) | null = null;
  onerror: ((event: ErrorEvent) => void) | null = null;
  onmessageerror: (() => void) | null = null;
  stopped = false;
  command?: SttvOpenCommand;
  postMessage(command: SttvOpenCommand) { this.command = command; }
  terminate() { this.stopped = true; }
  send(message: Omit<SttvWorkerMessage, 'operationId'> & Record<string, unknown>, operationId = this.command!.operationId) {
    this.onmessage?.({ data: { ...message, operationId } } as MessageEvent<SttvWorkerMessage>);
  }
}
function sttvHarness() {
  const workers: SttvFakeWorker[] = [];
  const controller = new SttvOpeningController(() => {}, () => {
    const worker = new SttvFakeWorker(); workers.push(worker); return worker as SttvWorkerPort;
  });
  return { workers, controller, file: new File(['{}'], 'example.json') };
}
const sttvData = sttvAdaptSet(sttvSet(sttvDatabase([sttvTechnology('a')])), sttvSetFiles());

test('empty picker selection preserves an existing ready set and its worker', () => {
  const { controller, workers, file } = sttvHarness();
  controller.open([file, file, file]);
  workers[0].send({ type: 'ready', data: sttvData });
  const previous = controller.state;
  controller.open([]);
  assert.equal(controller.state, previous);
  assert.equal(workers[0].stopped, false);
  assert.equal(workers.length, 1);
});

test('only the current worker and operation can publish, once', () => {
  const { controller, workers, file } = sttvHarness();
  controller.open([file, file, file]); controller.open([file, file, file]);
  assert.equal(workers[0].stopped, true);
  workers[0].send({ type: 'ready', data: sttvData });
  workers[1].send({ type: 'ready', data: sttvData }, 1);
  assert.equal(controller.state.status, 'loading');
  workers[1].send({ type: 'ready', data: sttvData });
  assert.equal(controller.state.status, 'ready');
  assert.equal(workers[1].stopped, false);
  workers[1].send({ type: 'error', error: sttvDiagnostic('worker_failed', null), diagnostics: [] });
  assert.equal(controller.state.status, 'ready');
  controller.dispose(); assert.equal(workers[1].stopped, true);
});
test('cancel clears the attempt, including late messages', () => {
  const { controller, workers, file } = sttvHarness();
  controller.open([file, file, file]); controller.cancel();
  workers[0].send({ type: 'ready', data: sttvData });
  assert.equal(controller.state.status, 'idle');
  assert.deepEqual(controller.state.files, []);
  assert.equal(controller.state.data, null);
  assert.equal(workers[0].stopped, true);
});
test('errors release the worker and retain the File for explicit retry', () => {
  const { controller, workers, file } = sttvHarness();
  controller.open([file, file, file]);
  workers[0].send({ type: 'error', error: sttvDiagnostic('invalid_json', 'parsing'), diagnostics: [] });
  assert.equal(controller.state.status, 'error'); assert.equal(workers[0].stopped, true);
  controller.retry();
  assert.equal(workers[1].command?.files[0], file);
  assert.equal(workers[1].command?.operationId, 2);
  assert.equal(controller.state.error, null);
});
test('worker startup failure becomes a reportable error', () => {
  const controller = new SttvOpeningController(() => {}, () => { throw new Error('Unavailable worker'); });
  controller.open([new File(['{}'], 'db.json')]);
  assert.equal(controller.state.status, 'error');
  assert.equal(controller.state.error?.code, 'worker_failed');
});
test('empty results retain their worker and export only current diagnostics', () => {
  const { controller, workers, file } = sttvHarness();
  assert.throws(() => sttvBuildReport(controller.state));
  controller.open([file, file, file]);
  workers[0].send({ type: 'ready', data: sttvAdaptSet(sttvSet(), sttvSetFiles()) });
  assert.equal(controller.state.status, 'empty'); assert.equal(workers[0].stopped, false);
  const report = sttvBuildReport(controller.state, new Date('2026-11-17T00:00:00Z'));
  assert.deepEqual(Object.keys(report), ['format', 'formatVersion', 'exportedAt', 'operationId', 'setId', 'files', 'counts', 'result', 'error', 'diagnostics']);
  assert.equal(report.files.length, 3);
  assert.equal(report.files[0].name, file.name);
  assert.equal(report.setId, 'a'.repeat(64));
  assert.equal(report.result, 'empty'); assert.equal(report.error, null);
});
