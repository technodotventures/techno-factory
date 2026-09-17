// Sanity: /docs/json still generates with the anyOf observe schema.
const REPO = '/opt/data/dev-workspaces/worktrees/pod-run007';
const { mkdtemp } = await import('node:fs/promises');
const { tmpdir } = await import('node:os');
const path = await import('node:path');
const { buildApp } = await import(`${REPO}/dist/app.js`);
const { closeSmartwareCore } = await import(`${REPO}/dist/smartware/core.js`);

const dataDir = await mkdtemp(path.join(tmpdir(), 'pod-openapi-'));
const app = await buildApp({ host: '127.0.0.1', port: 0, dataDir, ownerId: undefined, podId: 'founder-test', podName: 'Founder Test Pod', apiToken: undefined, mcpClientEnabled: false, mcpDockerCommand: 'docker', mcpPortBase: 5100 }, false);

const res = await app.inject({ method: 'GET', url: '/docs/json' });
console.log('GET /docs/json →', res.statusCode);
const doc = JSON.parse(res.payload);
console.log('top-level keys:', Object.keys(doc).slice(0, 12).join(', '));
const paths = doc.paths ?? doc.swagger?.paths ?? doc.openapi?.paths;
if (!paths) {
  console.log('no paths object found; first 400 chars:', res.payload.slice(0, 400));
} else {
  const observe = paths['/pod/observe']?.post;
  console.log('paths included:', Object.keys(paths).length);
  console.log('observe summary:', observe?.summary);
  console.log('observe body schema has anyOf:', JSON.stringify(observe?.requestBody ?? null).includes('anyOf'));
}

await app.close();
await closeSmartwareCore();
