// run-009 evidence helper: capture a real GET /pod/telemetry/sources response.
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

import { buildApp } from '/opt/data/dev-workspaces/worktrees/pod-run007/dist/app.js';
import { closeDb, getDb, recordObjectMemoryObservation, upsertObject } from '/opt/data/dev-workspaces/worktrees/pod-run007/dist/pod/db.js';
import { closeSmartwareCore } from '/opt/data/dev-workspaces/worktrees/pod-run007/dist/smartware/core.js';

const dataDir = await mkdtemp(path.join(tmpdir(), 'run009-demo-'));
const env = {
  host: '127.0.0.1', port: 0, dataDir, ownerId: undefined,
  podId: 'run-009-demo', podName: 'Run 009 Demo', apiToken: undefined,
  mcpClientEnabled: false, mcpDockerCommand: 'docker', mcpPortBase: 5100,
};
const app = await buildApp(env, false);
const db = getDb(env);

upsertObject(db, {
  id: 'obj-demo-1', collection_id: 'journal', kind: 'note', title: 'Demo object',
  content: { text: 'demo' }, reflection_claim_count: 2,
});
for (const observationId of ['obs-demo-1', 'obs-demo-2']) {
  recordObjectMemoryObservation(db, {
    observation_id: observationId, object_id: 'obj-demo-1', object_version: 1,
    object_hash: `hash-${observationId}`, source_app: 'hermes',
    source_id: 'hermes-bookmarks:demo', scope: 'personal',
  });
}

const lane = await app.inject({ method: 'GET', url: '/pod/telemetry/sources?prefix=hermes-bookmarks%3A' });
console.log('GET /pod/telemetry/sources?prefix=hermes-bookmarks%3A ->', lane.statusCode);
console.log(lane.payload);
console.log();

const unknown = await app.inject({ method: 'GET', url: '/pod/telemetry/sources?source_id=ghost-lane:nothing' });
console.log('GET /pod/telemetry/sources?source_id=ghost-lane:nothing ->', unknown.statusCode);
console.log(unknown.payload);

await app.close();
await closeSmartwareCore();
closeDb();
