import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 1,
  workers: 1,
  reporter: 'list',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        // Use the pre-installed Chromium binary when the packaged headless shell is unavailable.
        ...(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH
          ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH }
          : {}),
      },
    },
  ],
  webServer: [
    {
      // Backend — serves /api/config, /api/demos, /api/health
      command:
        'cd ../backend && uv run uvicorn app.main:app --port 8001 --log-level warning',
      url: 'http://localhost:8001/api/health',
      reuseExistingServer: !process.env.CI,
      timeout: 30_000,
      env: {
        NEXT_PUBLIC_BACKEND_URL: 'http://localhost:8001',
        BACKEND_URL: 'http://localhost:8001',
      },
    },
    {
      // Frontend
      command: 'NEXT_PUBLIC_BACKEND_URL=http://localhost:8001 BACKEND_URL=http://localhost:8001 pnpm dev',
      url: 'http://localhost:3000',
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
  ],
});
