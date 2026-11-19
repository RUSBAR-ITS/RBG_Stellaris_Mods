import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: './',
  cacheDir: 'data/frontend-cache/vite',
  build: { outDir: 'data/frontend-build', emptyOutDir: true },
  server: { port: 5173, strictPort: true, watch: { ignored: ['**/data/**'] } },
});
