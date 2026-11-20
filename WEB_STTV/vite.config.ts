import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import service from './config/service.json' with { type: 'json' };

export default defineConfig({
  plugins: [react()],
  base: './',
  cacheDir: 'data/frontend-cache/vite',
  build: { outDir: 'data/frontend-build', emptyOutDir: true },
  server: { port: 5173, strictPort: true, watch: { ignored: ['**/data/**'] },
    proxy: { [service.prefix]: { target: `http://${service.host}:${service.port}` } } },
});
