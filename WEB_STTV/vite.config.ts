import { sttvWorkPath } from './frontend-workspace.ts';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: './',
  cacheDir: sttvWorkPath('frontend-cache/vite'),
  build: { outDir: sttvWorkPath('frontend-build'), emptyOutDir: true },
  server: { port: 5173, strictPort: true, watch: { ignored: ['**/data/**'] },
    proxy: {
      '/api/trees': process.env.STTV_SERVER_URL ?? 'http://127.0.0.1:8788',
      '/api/localization': process.env.STTV_SERVER_URL ?? 'http://127.0.0.1:8788' } },
});
