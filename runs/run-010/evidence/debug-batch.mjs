// Debug: what does the batch route actually return?
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { buildApp } from '/opt/data/dev-workspaces/worktrees/pod-run007/dist/app.js';
import { closeSmartwareCore } from '/opt/data/dev-workspaces/worktrees/pod-run007/dist/smartware/core.js';

const dataDir = await mkdtemp(path.join(tmpdir(), 'pod-debug-'));
const env = {
  host: '127.0.0.1', port: 0, dataDir, ownerId: undefined, podId: 'founder-test',
  podName: 'Founder Test Pod', apiToken: undefined, mcpClientEnabled: false,
  mcpDockerCommand: 'docker', mcpPortBase: 5100,
};
const app = await buildApp(env, false);
let n = 9000;
const op = () => `op_${String(n++).padStart(26, '0')}`;

for (const withSourceId of [false, true]) {
  const items = Array.from({ length: 3 }, (_, i) => ({
    operation_id: op(),
    content: `Debug payload ${i}`,
    ...(withSourceId ? { source_id: 'lane:debug' } : {}),
  }));
  const res = await app.inject({ method: 'POST', url: '/pod/observe', payload: { actor_id: 'person-local', items } });
  console.log('withSourceId =', withSourceId, 'status', res.statusCode);
  console.log(JSON.stringify(JSON.parse(res.payload), null, 2));
}
await app.close();
await closeSmartwareCore();
