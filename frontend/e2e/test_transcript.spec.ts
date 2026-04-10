import { test, expect } from '@playwright/test';

test.describe('TranscriptPanel', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/demo/sales');
    await page.waitForSelector('[data-testid="transcript-panel"]', { timeout: 10_000 });
  });

  test('injecting a transcript entry via DOM event causes it to appear in the panel', async ({
    page,
  }) => {
    // No entries initially
    await expect(page.getByTestId('transcript-entry')).toHaveCount(0);

    // Inject one entry
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__transcript_entry__', {
          detail: { speaker: 'Agent', text: 'Hello, how can I help you today?', timestamp: Date.now() },
        })
      );
    });

    // Entry should appear
    await expect(page.getByTestId('transcript-entry')).toHaveCount(1);
    await expect(page.getByTestId('transcript-entry').first()).toContainText(
      'Hello, how can I help you today?'
    );
  });

  test('speaker label is rendered in uppercase mono style', async ({ page }) => {
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__transcript_entry__', {
          detail: { speaker: 'Agent', text: 'Testing speaker label', timestamp: Date.now() },
        })
      );
    });

    await expect(page.getByTestId('transcript-entry')).toHaveCount(1);
    const speakerEl = page.getByTestId('transcript-entry').locator('span').first();
    await expect(speakerEl).toContainText('AGENT');
  });

  test('auto-scroll: after 10 entries the scroll position is at the bottom', async ({ page }) => {
    // Inject 10 entries
    await page.evaluate(() => {
      for (let i = 0; i < 10; i++) {
        window.dispatchEvent(
          new CustomEvent('__transcript_entry__', {
            detail: {
              speaker: i % 2 === 0 ? 'Agent' : 'You',
              text: `Message number ${i + 1} — this is a longer text to ensure content overflows the scroll area and tests the auto-scroll behaviour correctly.`,
              timestamp: Date.now() + i * 1000,
            },
          })
        );
      }
    });

    // Wait for all 10 entries to render
    await expect(page.getByTestId('transcript-entry')).toHaveCount(10);

    // Check scroll position is at bottom
    const isScrolledToBottom = await page.evaluate(() => {
      const el = document.querySelector('[data-testid="transcript-scroll"]');
      if (!el) return false;
      return Math.abs(el.scrollHeight - el.scrollTop - el.clientHeight) < 5;
    });

    expect(isScrolledToBottom).toBe(true);
  });
});
