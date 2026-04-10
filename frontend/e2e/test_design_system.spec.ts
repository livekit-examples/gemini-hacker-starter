import { expect, test } from '@playwright/test';

test.describe('Design System Atoms', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/test-atoms');
  });

  test('Button primary renders with background color #4DA6FF', async ({ page }) => {
    const btn = page.getByTestId('btn-primary');
    await expect(btn).toBeVisible();
    const bgColor = await btn.evaluate((el) => window.getComputedStyle(el).backgroundColor);
    // #4DA6FF = rgb(77, 166, 255)
    expect(bgColor).toBe('rgb(77, 166, 255)');
  });

  test('Button muted has cursor-not-allowed', async ({ page }) => {
    const btn = page.getByTestId('btn-muted');
    await expect(btn).toBeVisible();
    const cursor = await btn.evaluate((el) => window.getComputedStyle(el).cursor);
    expect(cursor).toBe('not-allowed');
  });

  test('Card has border-radius >= 32px', async ({ page }) => {
    const card = page.getByTestId('card');
    await expect(card).toBeVisible();
    const radius = await card.evaluate((el) => {
      return parseFloat(window.getComputedStyle(el).borderRadius);
    });
    expect(radius).toBeGreaterThanOrEqual(32);
  });

  test('StatusDot with state="connected" contains a green element', async ({ page }) => {
    const dot = page.getByTestId('status-connected');
    await expect(dot).toBeVisible();
    // The first <span> child is the colored dot
    const dotSpan = dot.locator('span').first();
    const color = await dotSpan.evaluate((el) => window.getComputedStyle(el).backgroundColor);
    // Tailwind green-400 = #4ade80 = rgb(74, 222, 128)
    expect(color).toBe('rgb(74, 222, 128)');
  });

  test('Avatar with initials "AR" renders those characters', async ({ page }) => {
    const avatar = page.getByTestId('avatar-ar');
    await expect(avatar).toBeVisible();
    await expect(avatar).toContainText('AR');
  });
});
