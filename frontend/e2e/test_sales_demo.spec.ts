import { test, expect } from '@playwright/test';

test.describe('Sales Demo — Session 15', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/demo/sales');
    await page.waitForSelector('[data-testid="dashboard-layout"]', { timeout: 10_000 });
  });

  // -------------------------------------------------------------------------
  // Basic page load
  // -------------------------------------------------------------------------

  test('/demo/sales loads without error', async ({ page }) => {
    await expect(page).toHaveURL('/demo/sales');
    await expect(page.getByTestId('dashboard-layout')).toBeVisible();
  });

  // -------------------------------------------------------------------------
  // PersonaCard — Aria
  // -------------------------------------------------------------------------

  test('PersonaCard shows "Aria"', async ({ page }) => {
    await expect(page.getByTestId('persona-name')).toContainText('Aria');
  });

  test('PersonaCard shows "Senior Sales Strategist" role', async ({ page }) => {
    await expect(page.getByTestId('persona-role')).toContainText('Sales Strategist');
  });

  test('PersonaCard shows initials "AR"', async ({ page }) => {
    await expect(page.getByTestId('persona-initials')).toContainText('AR');
  });

  // -------------------------------------------------------------------------
  // SalesPanel is present
  // -------------------------------------------------------------------------

  test('SalesPanel is rendered instead of generic ToolOutputPanel', async ({ page }) => {
    await expect(page.getByTestId('sales-panel')).toBeVisible();
    // Generic ToolOutputPanel should NOT be on the sales page
    await expect(page.getByTestId('tool-output-panel')).toHaveCount(0);
  });

  // -------------------------------------------------------------------------
  // Talking-points card via talking_points tool output
  // -------------------------------------------------------------------------

  test('talking_points tool output renders bullet list in SalesPanel', async ({ page }) => {
    // Ensure panel is fully mounted before dispatching event
    await expect(page.getByTestId('sales-panel')).toBeVisible();
    await page.waitForTimeout(200);
    await expect(page.getByTestId('sales-talking-points-card')).toHaveCount(0);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'talking_points',
            points: ['Lead with ROI story', 'Address security objection', 'Confirm budget cycle'],
            count: 3,
          },
        })
      );
    });

    await expect(page.getByTestId('sales-talking-points-card')).toHaveCount(1);
    // The three talking points should be visible
    const card = page.getByTestId('sales-talking-points-card');
    await expect(card).toContainText('Lead with ROI story');
    await expect(card).toContainText('Address security objection');
    await expect(card).toContainText('Confirm budget cycle');
  });

  // -------------------------------------------------------------------------
  // Priority badge colour via analyze_screen_content output
  // -------------------------------------------------------------------------

  test('high priority badge has correct colour class', async ({ page }) => {
    await expect(page.getByTestId('sales-panel')).toBeVisible();
    await page.waitForTimeout(200);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'talking_points',
            priority: 'high',
            findings: ['Competitor present in the deal notes.'],
            recommendations: ['Escalate to the economic buyer immediately.'],
          },
        })
      );
    });

    // Wait for the badge to appear with the expected priority
    const badge = page.getByTestId('priority-badge');
    await expect(badge).toHaveAttribute('data-priority', 'high');
    await expect(badge).toContainText('high');
    // Red colour class should be applied
    const cls = await badge.getAttribute('class');
    expect(cls).toContain('red');
  });

  test('medium priority badge renders correctly', async ({ page }) => {
    await expect(page.getByTestId('sales-panel')).toBeVisible();
    await page.waitForTimeout(200);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'talking_points',
            priority: 'medium',
            findings: ['Deal at proposal stage.'],
            recommendations: ['Follow up within 24 hours.'],
          },
        })
      );
    });

    const badge = page.getByTestId('priority-badge');
    await expect(badge).toHaveAttribute('data-priority', 'medium');
    const cls = await badge.getAttribute('class');
    expect(cls).toContain('amber');
  });

  test('low priority badge renders correctly', async ({ page }) => {
    await expect(page.getByTestId('sales-panel')).toBeVisible();
    await page.waitForTimeout(200);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'talking_points',
            priority: 'low',
            findings: ['Early-stage discovery deal.'],
            recommendations: ['Nurture with light-touch follow-ups.'],
          },
        })
      );
    });

    const badge = page.getByTestId('priority-badge');
    await expect(badge).toHaveAttribute('data-priority', 'low');
    const cls = await badge.getAttribute('class');
    expect(cls).toContain('green');
  });

  // -------------------------------------------------------------------------
  // Proposal section card
  // -------------------------------------------------------------------------

  test('proposal_section tool output renders formatted card', async ({ page }) => {
    // Ensure the SalesPanel is fully mounted before dispatching the event
    await expect(page.getByTestId('sales-panel')).toBeVisible();
    await page.waitForTimeout(200);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'proposal_section',
            section: 'executive_summary',
            content: 'This proposal outlines how Hartmann Industries can accelerate growth.',
            context: 'Hartmann Industries — mid-size manufacturing firm in Stuttgart',
          },
        })
      );
    });

    await expect(page.getByTestId('sales-proposal-card')).toHaveCount(1);
    const card = page.getByTestId('sales-proposal-card');
    await expect(card).toContainText('Executive Summary');
    await expect(card).toContainText('Hartmann Industries can accelerate growth');
  });

  // -------------------------------------------------------------------------
  // Multiple outputs stack
  // -------------------------------------------------------------------------

  test('multiple tool outputs stack in SalesPanel', async ({ page }) => {
    await expect(page.getByTestId('sales-panel')).toBeVisible();
    await page.waitForTimeout(200);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: { type: 'talking_points', points: ['Point A'] },
        })
      );
    });
    await expect(page.getByTestId('sales-talking-points-card')).toHaveCount(1);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: { type: 'talking_points', points: ['Point B'] },
        })
      );
    });
    await expect(page.getByTestId('sales-talking-points-card')).toHaveCount(2);
  });

  // -------------------------------------------------------------------------
  // Demo scenarios visible in DemoGuidePanel
  // -------------------------------------------------------------------------

  test('DemoGuidePanel shows sales scenarios', async ({ page }) => {
    const guidePanel = page.getByTestId('demo-guide-panel');
    await expect(guidePanel).toBeVisible();
    // At least one scenario title should be present
    await expect(guidePanel).toContainText('Competitive Deal');
  });
});
