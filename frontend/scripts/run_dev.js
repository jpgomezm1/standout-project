/**
 * Start the Next.js dev server on a free port.
 *
 * Usage:
 *   cd frontend && node scripts/run_dev.js
 */

const net = require('net');
const { execSync, spawn } = require('child_process');
const path = require('path');

const DEFAULT_PORT = parseInt(process.env.FRONTEND_PORT || '3000', 10);
const MAX_TRIES = 10;

function isPortFree(port) {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.once('error', () => resolve(false));
    server.once('listening', () => {
      server.close();
      resolve(true);
    });
    server.listen(port, '127.0.0.1');
  });
}

async function findFreePort(start) {
  for (let i = 0; i < MAX_TRIES; i++) {
    const port = start + i;
    if (await isPortFree(port)) return port;
  }
  throw new Error(`No free port found in range ${start}–${start + MAX_TRIES - 1}`);
}

async function main() {
  const port = await findFreePort(DEFAULT_PORT);

  if (port !== DEFAULT_PORT) {
    console.log(`[run_dev] Puerto ${DEFAULT_PORT} ocupado → usando ${port}`);
  } else {
    console.log(`[run_dev] Iniciando frontend en puerto ${port}`);
  }

  const child = spawn('npx', ['next', 'dev', '-p', String(port)], {
    stdio: 'inherit',
    shell: true,
    cwd: path.resolve(__dirname, '..'),
  });

  child.on('exit', (code) => process.exit(code || 0));
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
