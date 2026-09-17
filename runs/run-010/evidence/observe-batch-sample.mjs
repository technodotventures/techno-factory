// run-010 evidence: real batch request/response against the built Pod app.
//
//   node evidence/observe-batch-sample.mjs
//
// Prints (1) a mixed batch (accepted + duplicate + rejected) request and its raw
// response, and (2) one 100-item batch vs 100 sequential single-operation calls.
const REPO = '/opt/data/dev-workspaces/worktrees/pod-run007';

const { mkdtemp, rm } = await import('node:fs/promises');
const { tmpdir } = await import('node:os');
const path = await import('node:path');
const { buildApp } = await import(`${REPO}/dist/app.js`);
const { closeSmartwareCore } = await import(`${REPO}/dist/smartware/core.js`);

const dataDir = await mkdtemp(path.join(tmpdir(), 'pod-observe-batch-sample-'));

// Pod's host guard only accepts the configured loopback port, and it captures
// that allowlist when the app is built — so pick the port up front.
const net = await import('node:net');
const listenPort = await new Promise(resolve => {
  const probe = net.createServer();
  probe.listen(0, '127.0.0.1', () => {
    const port = probe.address().port;
    probe.close(() => resolve(port));
  });
});

const env = {
  host: '127.0.0.1',
  port: listenPort,
  dataDir,
  ownerId: undefined,
  podId: 'founder-test',
  podName: 'Founder Test Pod',
  apiToken: undefined,
  mcpClientEnabled: false,
  mcpDockerCommand: 'docker',
  mcpPortBase: 5100,
};
const app = await buildApp(env, false);
let n = 70000;
const op = () => `op_${String(n++).padStart(26, '0')}`;

const post = payload => app.inject({ method: 'POST', url: '/pod/observe', payload });

// ── 1. Mixed batch: one malformed operation_id, one duplicate, one accepted ──
const shared = op();
const mixed = {
  actor_id: 'person-local',
  items: [
    { operation_id: shared, content: 'Lane backfill: research entry 192.', source_id: 'lane:research:192' },
    { operation_id: shared, content: 'Lane backfill: research entry 192.', source_id: 'lane:research:192' },
    { operation_id: 'NOT-A-OPERATION-ID', content: 'Malformed item.' },
  ],
};
const mixedResponse = await post(mixed);
console.log('── REQUEST ── POST /pod/observe');
console.log(JSON.stringify(mixed, null, 2));
console.log(`\n── RESPONSE ── HTTP ${mixedResponse.statusCode}`);
console.log(JSON.stringify(JSON.parse(mixedResponse.payload), null, 2));

// ── 2. One 100-item batch vs 100 sequential single-operation calls ──────────
const bulkItems = Array.from({ length: 100 }, (_, i) => ({
  operation_id: op(),
  content: `Bulk importer artifact ${i}`,
  source_id: `lane:perf:${i}`,
}));

const batchStarted = Date.now();
const batchResponse = await post({ actor_id: 'person-local', items: bulkItems });
const batchMs = Date.now() - batchStarted;

const sequentialStarted = Date.now();
for (let i = 0; i < 100; i += 1) {
  const single = await post({
    actor_id: 'person-local',
    operation_id: op(),
    content: `Sequential artifact ${i}`,
    source_id: `lane:perf-sequential:${i}`,
  });
  if (single.statusCode !== 200) throw new Error(`sequential call ${i} failed: ${single.statusCode}`);
}
const sequentialMs = Date.now() - sequentialStarted;

const batchBody = JSON.parse(batchResponse.payload);
console.log('\n── TIMING ── 100 artifacts (in-process inject)');
console.log(`one batched request : HTTP ${batchResponse.statusCode} · ${batchBody.results.length} per-item outcomes · ${batchMs} ms`);
console.log(`100 sequential calls: ${sequentialMs} ms`);
console.log(`speedup             : ${(sequentialMs / batchMs).toFixed(2)}x`);

// ── 3. Same comparison over a real transport (loopback HTTP), which is what the
//      270-call backfill actually paid: one round trip vs 100 round trips.
//      (In-process inject calls stop working once the real server is listening.) ─
await app.listen({ host: '127.0.0.1', port: listenPort });
const base = `http://127.0.0.1:${listenPort}`;
const httpPost = async payload => {
  const response = await fetch(`${base}/pod/observe`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return { status: response.status, body: await response.json() };
};

const httpBatchItems = Array.from({ length: 100 }, (_, i) => ({
  operation_id: op(),
  content: `HTTP batch artifact ${i}`,
  source_id: `lane:http:${i}`,
}));
const httpBatchStarted = Date.now();
const httpBatch = await httpPost({ actor_id: 'person-local', items: httpBatchItems });
const httpBatchMs = Date.now() - httpBatchStarted;

const httpSequentialStarted = Date.now();
for (let i = 0; i < 100; i += 1) {
  const single = await httpPost({
    actor_id: 'person-local',
    operation_id: op(),
    content: `HTTP sequential artifact ${i}`,
    source_id: `lane:http-sequential:${i}`,
  });
  if (single.status !== 200) throw new Error(`sequential call ${i} failed: ${single.status}`);
}
const httpSequentialMs = Date.now() - httpSequentialStarted;

console.log('\n── TIMING ── 100 artifacts (loopback HTTP)');
console.log(`one batched request : HTTP ${httpBatch.status} · ${httpBatch.body.results.length} per-item outcomes · ${httpBatchMs} ms`);
console.log(`100 sequential calls: ${httpSequentialMs} ms`);
console.log(`speedup             : ${(httpSequentialMs / httpBatchMs).toFixed(2)}x`);

await app.close();
await closeSmartwareCore();
await rm(dataDir, { recursive: true, force: true });
