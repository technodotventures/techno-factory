// run-010 perf receipt: multi-repeat measurement over loopback HTTP.
//   100-item batch vs 100 sequential single calls, 5 repeats each (median + range),
//   then the brief's real workload shape: 270 items (3 batched requests vs 270 calls).
const REPO = '/opt/data/dev-workspaces/worktrees/pod-run007';

const { mkdtemp, rm } = await import('node:fs/promises');
const { tmpdir } = await import('node:os');
const path = await import('node:path');
const { buildApp } = await import(`${REPO}/dist/app.js`);
const { closeSmartwareCore } = await import(`${REPO}/dist/smartware/core.js`);

const dataDir = await mkdtemp(path.join(tmpdir(), 'pod-observe-perf-receipt-'));
const net = await import('node:net');
const listenPort = await new Promise(resolve => {
  const probe = net.createServer();
  probe.listen(0, '127.0.0.1', () => {
    const port = probe.address().port;
    probe.close(() => resolve(port));
  });
});

const env = {
  host: '127.0.0.1', port: listenPort, dataDir, ownerId: undefined,
  podId: 'founder-test', podName: 'Founder Test Pod', apiToken: undefined,
  mcpClientEnabled: false, mcpDockerCommand: 'docker', mcpPortBase: 5100,
};
const app = await buildApp(env, false);
await app.listen({ host: '127.0.0.1', port: listenPort });
const base = `http://127.0.0.1:${listenPort}`;
let n = 90000;
const op = () => `op_${String(n++).padStart(26, '0')}`;
const post = async payload => {
  const response = await fetch(`${base}/pod/observe`, {
    method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload),
  });
  return { status: response.status, body: await response.json() };
};

const median = arr => [...arr].sort((a, b) => a - b)[Math.floor(arr.length / 2)];
const fmt = arr => `median ${median(arr)} ms (runs: ${arr.join(', ')} ms)`;

// ── 100-item: 5 repeats each side ──────────────────────────────────────────
const batchTimes = [], seqTimes = [];
for (let r = 0; r < 5; r += 1) {
  const items = Array.from({ length: 100 }, (_, i) => ({ operation_id: op(), content: `B${r}-${i}`, source_id: `perf:b:${r}:${i}` }));
  const t0 = Date.now();
  const b = await post({ actor_id: 'person-local', items });
  batchTimes.push(Date.now() - t0);
  if (b.status !== 200 || b.body.results.length !== 100) throw new Error(`batch run ${r}: HTTP ${b.status}`);
  const t1 = Date.now();
  for (let i = 0; i < 100; i += 1) {
    const s = await post({ actor_id: 'person-local', operation_id: op(), content: `S${r}-${i}`, source_id: `perf:s:${r}:${i}` });
    if (s.status !== 200) throw new Error(`seq run ${r} item ${i}: HTTP ${s.status}`);
  }
  seqTimes.push(Date.now() - t1);
}
const batchMed = median(batchTimes), seqMed = median(seqTimes);

console.log('── PERF RECEIPT ── 100 artifacts per run, loopback HTTP, 5 repeats');
console.log(`1 batched request  : ${fmt(batchTimes)}`);
console.log(`100 sequential calls: ${fmt(seqTimes)}`);
console.log(`median speedup      : ${(seqMed / batchMed).toFixed(2)}x`);

// ── The brief's workload: 270 items ────────────────────────────────────────
const mkItems = (start, count) => Array.from({ length: count }, (_, i) => ({ operation_id: op(), content: `Backfill ${start + i}`, source_id: `perf:backfill:${start + i}` }));
const t2 = Date.now();
for (const [start, count] of [[0, 100], [100, 100], [200, 70]]) {
  const b = await post({ actor_id: 'person-local', items: mkItems(start, count) });
  if (b.status !== 200) throw new Error(`270-batch chunk failed: HTTP ${b.status}`);
}
const batched270 = Date.now() - t2;
const t3 = Date.now();
for (let i = 0; i < 270; i += 1) {
  const s = await post({ actor_id: 'person-local', operation_id: op(), content: `Seq backfill ${i}`, source_id: `perf:seq-backfill:${i}` });
  if (s.status !== 200) throw new Error(`270-seq item ${i}: HTTP ${s.status}`);
}
const sequential270 = Date.now() - t3;

console.log('\n── REAL WORKLOAD ── 270 artifacts (the lane-backfill shape)');
console.log(`3 batched requests (100+100+70): ${batched270} ms`);
console.log(`270 sequential single calls    : ${sequential270} ms`);
console.log(`speedup                        : ${(sequential270 / batched270).toFixed(2)}x`);
console.log(`round trips eliminated         : 270 → 3`);

await app.close();
await closeSmartwareCore();
await rm(dataDir, { recursive: true, force: true });
