import test from 'node:test';
import assert from 'node:assert/strict';
import { SttvOpeningController, type SttvWorkerPort } from '../../src/frontend/workers/controller';
import { sttvDiagnostic } from '../../src/frontend/workers/diagnostics';
import { sttvBuildReport } from '../../src/frontend/app/report';
import { sttvAdaptDatabase } from '../../src/frontend/data/adapter';
import type { SttvWorkerMessage, SttvOpenCommand } from '../../src/frontend/workers/protocol';
import { sttvDatabase, sttvTechnology } from './fixtures';

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
const sttvData = sttvAdaptDatabase(sttvDatabase([sttvTechnology('a')]));

test('only the current worker and operation can publish, once', () => {
  const { controller, workers, file } = sttvHarness();
  controller.open(file); controller.open(file);
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
  controller.open(file); controller.cancel();
  workers[0].send({ type: 'ready', data: sttvData });
  assert.equal(controller.state.status, 'idle');
  assert.equal(controller.state.file, null);
  assert.equal(controller.state.data, null);
  assert.equal(workers[0].stopped, true);
});
test('errors release the worker and retain the File for explicit retry', () => {
  const { controller, workers, file } = sttvHarness();
  controller.open(file);
  workers[0].send({ type: 'error', error: sttvDiagnostic('invalid_json', 'parsing'), diagnostics: [] });
  assert.equal(controller.state.status, 'error'); assert.equal(workers[0].stopped, true);
  controller.retry();
  assert.equal(workers[1].command?.file, file);
  assert.equal(workers[1].command?.operationId, 2);
  assert.equal(controller.state.error, null);
});
test('worker startup failure becomes a reportable error', () => {
  const controller = new SttvOpeningController(() => {}, () => { throw new Error('Unavailable worker'); });
  controller.open(new File(['{}'], 'db.json'));
  assert.equal(controller.state.status, 'error');
  assert.equal(controller.state.error?.code, 'worker_failed');
});
test('empty results retain their worker and export only current diagnostics', () => {
  const { controller, workers, file } = sttvHarness();
  assert.throws(() => sttvBuildReport(controller.state));
  controller.open(file);
  workers[0].send({ type: 'ready', data: sttvAdaptDatabase(sttvDatabase([])) });
  assert.equal(controller.state.status, 'empty'); assert.equal(workers[0].stopped, false);
  const report = sttvBuildReport(controller.state, new Date('2026-11-17T00:00:00Z'));
  assert.deepEqual(Object.keys(report), ['format', 'formatVersion', 'exportedAt', 'operationId', 'file', 'result', 'error', 'diagnostics']);
  assert.deepEqual(report.file, { name: file.name, size: file.size });
  assert.equal(report.result, 'empty'); assert.equal(report.error, null);
});
