import { sttvWorkPath } from './frontend-workspace.ts';
import { defineConfig } from '@playwright/test';

const sttvPreview = process.env.STTV_PREVIEW === '1';
const sttvUrl = `http://127.0.0.1:${sttvPreview ? 4173 : 5173}`;
export default defineConfig({
  testDir: 'tests/frontend/browser', fullyParallel: false, workers: 1,
  timeout: 60000, expect: { timeout: 10000 },
  outputDir: sttvWorkPath('frontend-tests/browser'),
  reporter: [['list'], ['json', { outputFile: sttvWorkPath('frontend-tests/browser-report.json') }]],
  use: { baseURL: sttvUrl, viewport: { width: 1440, height: 900 },
    screenshot: 'only-on-failure', trace: 'retain-on-failure' },
  webServer: { command: sttvPreview ? 'npm run preview -- --port 4173 --strictPort' : 'npm run dev',
    url: sttvUrl, reuseExistingServer: false },
});
