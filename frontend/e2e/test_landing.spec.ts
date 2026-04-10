import { test, expect } from '@playwright/test';

test.describe('Landing Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('page title contains "EXODIA"', async ({ page }) => {
    await expect(page).toHaveTitle(/exodia/i);
  });

  test('exactly 5 demo cards rendered', async ({ page }) => {
    const cards = page.getByTestId('demo-card');
    await expect(cards).toHaveCount(5);
  });

  test('each card has an avatar, a persona name, and at least one language tag', async ({
    page,
  }) => {
    const cards = page.getByTestId('demo-card');
    const count = await cards.count();
    expect(count).toBe(5);

    for (let i = 0; i < count; i++) {
      const card = cards.nth(i);
      await expect(card.getByTestId('avatar')).toBeVisible();
      await expect(card.getByTestId('persona-name')).toBeVisible();
      const langTags = card.getByTestId('language-tag');
      const langCount = await langTags.count();
      expect(langCount).toBeGreaterThanOrEqual(1);
    }
  });

  test('"View Demo" link on available cards; disabled button on unavailable cards', async ({
    page,
  }) => {
    // Sales is the only available demo — must have at least one "View Demo"
    await expect(page.getByText('View Demo').first()).toBeVisible();

    // At least one "Coming Soon" disabled button (manufacturing, logistics, real_estate, dental)
    const comingSoon = page.getByRole('button', { name: /coming soon/i });
    await expect(comingSoon.first()).toBeVisible();
    const firstDisabled = await comingSoon.first().getAttribute('disabled');
    expect(firstDisabled).not.toBeNull();
  });

  test('no element with text "lorem" or "placeholder"', async ({ page }) => {
    const bodyText = await page.locator('body').innerText();
    expect(bodyText.toLowerCase()).not.toContain('lorem');
    expect(bodyText.toLowerCase()).not.toContain('placeholder');
  });

  test('"View Demo" link navigates to the correct demo route', async ({ page }) => {
    const viewDemoLink = page.getByRole('link', { name: /view.*demo/i }).first();
    const href = await viewDemoLink.getAttribute('href');
    expect(href).toMatch(/^\/demo\//);
  });

  test('hero contains "Voice Intelligence" headline', async ({ page }) => {
    await expect(page.getByRole('heading', { level: 1 })).toContainText('Voice');
    await expect(page.getByRole('heading', { level: 1 })).toContainText('Intelligence');
  });
});
