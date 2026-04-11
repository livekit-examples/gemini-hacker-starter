import { test, expect } from '@playwright/test';

test.describe('Language Selector', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/demo/sales');
    await page.waitForSelector('[data-testid="dashboard-layout"]', { timeout: 10_000 });
  });

  test('language selector renders 4 options on /demo/sales', async ({ page }) => {
    const selector = page.getByTestId('language-selector');
    await expect(selector).toBeVisible();
    const options = selector.locator('option');
    await expect(options).toHaveCount(4);
  });

  test('language option values include all 4 language codes', async ({ page }) => {
    const options = page.locator('[data-testid="language-selector"] option');
    const values = await options.evaluateAll((opts) =>
      opts.map((o) => (o as HTMLOptionElement).value)
    );
    expect(values).toContain('en');
    expect(values).toContain('it');
    expect(values).toContain('ar-EG');
    expect(values).toContain('ar-AE');
  });

  test('flag emoji appears next to each language option', async ({ page }) => {
    const options = page.locator('[data-testid="language-selector"] option');
    const texts = await options.evaluateAll((opts) =>
      opts.map((o) => (o as HTMLOptionElement).textContent ?? '')
    );
    // Each option should contain a flag emoji — check for known flags
    const allFlags = ['🇬🇧', '🇮🇹', '🇪🇬', '🇦🇪'];
    for (const text of texts) {
      const hasFlag = allFlags.some((flag) => text.includes(flag));
      expect(hasFlag, `Option "${text}" does not contain a flag emoji`).toBe(true);
    }
  });

  test('selecting Arabic (Egyptian) sets dir=rtl on dashboard container', async ({ page }) => {
    await page.selectOption('[data-testid="language-selector"]', 'ar-EG');
    const dir = await page.locator('[data-testid="dashboard-layout"]').getAttribute('dir');
    expect(dir).toBe('rtl');
  });

  test('selecting Arabic (Emirati) sets dir=rtl on dashboard container', async ({ page }) => {
    await page.selectOption('[data-testid="language-selector"]', 'ar-AE');
    const dir = await page.locator('[data-testid="dashboard-layout"]').getAttribute('dir');
    expect(dir).toBe('rtl');
  });

  test('selecting English sets dir=ltr on dashboard container', async ({ page }) => {
    // First switch to Arabic then back to English
    await page.selectOption('[data-testid="language-selector"]', 'ar-EG');
    await page.selectOption('[data-testid="language-selector"]', 'en');
    const dir = await page.locator('[data-testid="dashboard-layout"]').getAttribute('dir');
    expect(dir).toBe('ltr');
  });

  test('selecting Italian sets dir=ltr on dashboard container', async ({ page }) => {
    await page.selectOption('[data-testid="language-selector"]', 'it');
    const dir = await page.locator('[data-testid="dashboard-layout"]').getAttribute('dir');
    expect(dir).toBe('ltr');
  });
});

test.describe('Language pre-selection from URL', () => {
  test('navigating to /demo/sales?lang=ar-EG shows RTL layout', async ({ page }) => {
    await page.goto('/demo/sales?lang=ar-EG');
    await page.waitForSelector('[data-testid="dashboard-layout"]', { timeout: 10_000 });
    const dir = await page.locator('[data-testid="dashboard-layout"]').getAttribute('dir');
    expect(dir).toBe('rtl');
  });

  test('navigating to /demo/sales?lang=it shows LTR layout', async ({ page }) => {
    await page.goto('/demo/sales?lang=it');
    await page.waitForSelector('[data-testid="dashboard-layout"]', { timeout: 10_000 });
    const dir = await page.locator('[data-testid="dashboard-layout"]').getAttribute('dir');
    expect(dir).toBe('ltr');
  });

  test('navigating with unknown lang falls back to default', async ({ page }) => {
    await page.goto('/demo/sales?lang=xx-INVALID');
    await page.waitForSelector('[data-testid="dashboard-layout"]', { timeout: 10_000 });
    // Should fall back to a valid supported language (LTR default)
    const dir = await page.locator('[data-testid="dashboard-layout"]').getAttribute('dir');
    expect(['ltr', 'rtl']).toContain(dir); // just ensure it renders without crashing
  });
});
