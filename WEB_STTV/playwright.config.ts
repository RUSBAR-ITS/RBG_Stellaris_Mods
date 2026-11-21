import { sttvWorkPath } from './frontend-workspace.ts';
import { defineConfig } from '@playwright/test';

const sttvPreview = process.env.STTV_PREVIEW === '1';
const sttvUrl = process.env.STTV_TEST_URL ?? `http://127.0.0.1:${sttvPreview ? 4173 : 5173}`;
export default defineConfig({
  testDir: 'tests/frontend/browser', fullyParallel: false, workers: 1,
  timeout: 60000, expect: { timeout: 10000 },
  outputDir: sttvWorkPath('frontend-tests/reports/browser'),
  reporter: [['list'], ['json', { outputFile: sttvWorkPath('frontend-tests/reports/browser-report.json') }]],
  use: { baseURL: sttvUrl, launchOptions: { executablePath: process.env.STTV_BROWSER_EXECUTABLE }, viewport: { width: 1440, height: 900 },
    screenshot: 'only-on-failure', trace: 'retain-on-failure' },
  webServer: process.env.STTV_TEST_URL ? undefined : { command: sttvPreview ? 'npm run preview -- --port 4173 --strictPort' : 'npm run dev',
    url: sttvUrl, reuseExistingServer: false },
});
