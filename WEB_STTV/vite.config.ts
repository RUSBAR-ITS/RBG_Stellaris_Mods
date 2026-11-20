import { sttvWorkPath } from './frontend-workspace.ts';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import service from './config/service.json' with { type: 'json' };

export default defineConfig({
  plugins: [react()],
  base: './',
  cacheDir: sttvWorkPath('frontend-cache/vite'),
  build: { outDir: sttvWorkPath('frontend-build'), emptyOutDir: true },
  server: { port: 5173, strictPort: true, watch: { ignored: ['**/data/**'] },
    proxy: { [service.prefix]: { target: `http://${service.host}:${service.port}` } } },
});
