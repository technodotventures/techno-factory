// run-010 latency-scaling receipt: the batched win vs per-round-trip cost.
// 270-artifact workload through a delaying proxy (simulated network latency):
// each round trip +10 ms, then +25 ms. Per-item substrate work is identical in
// both forms; the batched form pays 3 round trips vs 270.
const REPO = '/opt/data/dev-workspaces/worktrees/pod-run007';

const { mkdtemp, rm } = await import('node:fs/promises');
const { tmpdir } = await import('node:os');
const path = await import('node:path');
const http = await import('node:http');
const net = await import('node:net');
const { buildApp } = await import(`${REPO}/dist/app.js`);
const { closeSmartwareCore } = await import(`${REPO}/dist/smartware/core.js`);

const dataDir = await mkdtemp(path.join(tmpdir(), 'pod-observe-latency-'));
const freePort = () => new Promise(resolve => {
  const probe = net.createServer();
  probe.listen(0, '127.0.0.1', () => { const p = probe.address().port; probe.close(() => resolve(p)); });
});
const appPort = await freePort();
const proxyPort = await freePort();

const env = {
  host: '127.0.0.1', port: appPort, dataDir, ownerId: undefined,
  podId: 'founder-test', podName: 'Founder Test Pod', apiToken: undefined,
  mcpClientEnabled: false, mcpDockerCommand: 'docker', mcpPortBase: 5100,
};
const app = await buildApp(env, false);
await app.listen({ host: '127.0.0.1', port: appPort });

// ── delaying proxy: forwards to the app, adds DELAY ms to each response ─────
let delayMs = 0;
const proxy = http.createServer((req, res) => {
  const chunks = [];
  req.on('data', c => chunks.push(c));
  req.on('end', () => {
    const body = Buffer.concat(chunks);
    const headers = { ...req.headers, host: `127.0.0.1:${appPort}`, 'content-length': body.length };
    const up = http.request({ host: '127.0.0.1', port: appPort, path: req.url, method: req.method, headers }, upstream => {
      const parts = [];
      upstream.on('data', c => parts.push(c));
      upstream.on('end', () => {
        setTimeout(() => {
          res.writeHead(upstream.statusCode, upstream.headers);
          res.end(Buffer.concat(parts));
        }, delayMs);
      });
    });
    up.end(body);
  });
});
await new Promise(resolve => proxy.listen(proxyPort, '127.0.0.1', resolve));
const base = `http://127.0.0.1:${proxyPort}`;

let n = 110000;
const op = () => `op_${String(n++).padStart(26, '0')}`;
const post = async payload => {
  const response = await fetch(`${base}/pod/observe`, {
    method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload),
  });
  return { status: response.status, body: await response.json() };
};

const mkItems = (tag, start, count) => Array.from({ length: count }, (_, i) => ({
  operation_id: op(), content: `${tag} ${start + i}`, source_id: `lat:${tag}:${start + i}`,
}));

console.log('── LATENCY-SCALING RECEIPT ── 270-artifact workload through a delaying proxy');
console.log('   (simulated network latency on loopback substrate; each round trip +D ms)\n');

for (const D of [10, 25]) {
  delayMs = D;
  const t0 = Date.now();
  for (const [start, count] of [[0, 100], [100, 100], [200, 70]]) {
    const b = await post({ actor_id: 'person-local', items: mkItems(`batch-d${D}`, start, count) });
    if (b.status !== 200) throw new Error(`batch chunk failed: HTTP ${b.status}`);
  }
  const batched = Date.now() - t0;
  const t1 = Date.now();
  for (let i = 0; i < 270; i += 1) {
    const s = await post({ actor_id: 'person-local', operation_id: op(), content: `seq-d${D} ${i}`, source_id: `lat:seq-d${D}:${i}` });
    if (s.status !== 200) throw new Error(`seq item ${i}: HTTP ${s.status}`);
  }
  const sequential = Date.now() - t1;
  console.log(`+${D} ms per round trip:`);
  console.log(`  3 batched requests (100+100+70): ${batched} ms`);
  console.log(`  270 sequential single calls    : ${sequential} ms`);
  console.log(`  speedup                        : ${(sequential / batched).toFixed(2)}x   (round trips 270 → 3, gap ≈ 267 × ${D} ms)\n`);
}

delayMs = 0;
await app.close();
await new Promise(resolve => proxy.close(resolve));
await closeSmartwareCore();
await rm(dataDir, { recursive: true, force: true });
