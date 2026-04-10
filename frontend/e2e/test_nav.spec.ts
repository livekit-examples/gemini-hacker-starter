import { test, expect } from '@playwright/test';

test.describe('ExodiaNav', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('nav element is position: fixed', async ({ page }) => {
    const nav = page.getByTestId('exodia-nav');
    await expect(nav).toBeVisible();
    const position = await nav.evaluate((el) => getComputedStyle(el).position);
    expect(position).toBe('fixed');
  });

  test('brand mark text contains "EXODIA"', async ({ page }) => {
    const nav = page.getByTestId('exodia-nav');
    await expect(nav).toContainText('EXODIA');
  });

  test('nav background contains backdrop-filter blur', async ({ page }) => {
    const nav = page.getByTestId('exodia-nav');
    const backdropFilter = await nav.evaluate(
      (el) => getComputedStyle(el).backdropFilter
    );
    expect(backdropFilter).toMatch(/blur/);
  });

  test('GSAP entrance completes — nav visible after 1.5s', async ({ page }) => {
    // Wait for the GSAP animation duration (0.9s) plus buffer
    await page.waitForTimeout(1500);
    const nav = page.getByTestId('exodia-nav');
    await expect(nav).toBeVisible();
    const opacity = await nav.evaluate((el) => getComputedStyle(el).opacity);
    // After clearProps the inline opacity is removed so computed value is '1'
    expect(parseFloat(opacity)).toBeCloseTo(1, 1);
  });
});
