import { test, expect } from '@playwright/test';

test.describe('Dashboard Layout', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/demo/sales');
    // Wait for the dashboard layout to mount
    await page.waitForSelector('[data-testid="dashboard-layout"]', { timeout: 10_000 });
  });

  test('three panels rendered on /demo/sales', async ({ page }) => {
    await expect(page.getByTestId('dashboard-left')).toBeVisible();
    await expect(page.getByTestId('dashboard-center')).toBeVisible();
    await expect(page.getByTestId('dashboard-right')).toBeVisible();
  });

  test('PersonaCard shows "Aria" for the sales demo', async ({ page }) => {
    await expect(page.getByTestId('persona-name')).toContainText('Aria');
  });

  test('SessionControls contains disconnect and reset buttons', async ({ page }) => {
    const controls = page.getByTestId('session-controls');
    await expect(controls).toBeVisible();
    await expect(page.getByTestId('disconnect-button')).toBeVisible();
    await expect(page.getByTestId('reset-button')).toBeVisible();
  });

  test('language selector contains all 4 language options', async ({ page }) => {
    const selector = page.getByTestId('language-selector');
    await expect(selector).toBeVisible();

    const options = selector.locator('option');
    await expect(options).toHaveCount(4);

    const values = await options.evaluateAll((opts) =>
      opts.map((o) => (o as HTMLOptionElement).value)
    );
    expect(values).toContain('en');
    expect(values).toContain('it');
    expect(values).toContain('ar-EG');
    expect(values).toContain('ar-AE');
  });

  test('ToolOutputPanel renders a card when a tool-output DOM event is dispatched', async ({
    page,
  }) => {
    // Verify panel is present and empty initially
    await expect(page.getByTestId('tool-output-panel')).toBeVisible();
    await expect(page.getByTestId('tool-output-card')).toHaveCount(0);

    // Simulate a tool-output message via the test injection event
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: { type: 'talking_points', points: ['Build rapport', 'Ask about Q4'] },
        })
      );
    });

    // Card should appear
    await expect(page.getByTestId('tool-output-card')).toHaveCount(1);
  });

  test('TranscriptPanel is visible', async ({ page }) => {
    await expect(page.getByTestId('transcript-panel')).toBeVisible();
  });

  test('VoiceActivity indicator is rendered', async ({ page }) => {
    await expect(page.getByTestId('voice-activity')).toBeVisible();
  });

  test('/demo/unknown redirects to /', async ({ page }) => {
    await page.goto('/demo/unknown_industry_that_does_not_exist');
    await expect(page).toHaveURL('/');
  });
});
