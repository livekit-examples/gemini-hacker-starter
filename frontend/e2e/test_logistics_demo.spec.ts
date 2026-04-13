import { test, expect } from '@playwright/test';

test.describe('Logistics Demo — Session 19', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/demo/logistics');
    await page.waitForSelector('[data-testid="dashboard-layout"]', { timeout: 10_000 });
  });

  // -------------------------------------------------------------------------
  // Basic page load
  // -------------------------------------------------------------------------

  test('/demo/logistics loads without error', async ({ page }) => {
    await expect(page).toHaveURL('/demo/logistics');
    await expect(page.getByTestId('dashboard-layout')).toBeVisible();
  });

  // -------------------------------------------------------------------------
  // PersonaCard — Elena
  // -------------------------------------------------------------------------

  test('PersonaCard shows "Elena"', async ({ page }) => {
    await expect(page.getByTestId('persona-name')).toContainText('Elena');
  });

  test('PersonaCard shows "Head of Logistics Operations" role', async ({ page }) => {
    await expect(page.getByTestId('persona-role')).toContainText('Logistics Operations');
  });

  test('PersonaCard shows initials "EL"', async ({ page }) => {
    await expect(page.getByTestId('persona-initials')).toContainText('EL');
  });

  // -------------------------------------------------------------------------
  // LogisticsPanel is present
  // -------------------------------------------------------------------------

  test('LogisticsPanel is rendered instead of generic ToolOutputPanel', async ({ page }) => {
    await expect(page.getByTestId('logistics-panel')).toBeVisible();
    await expect(page.getByTestId('tool-output-panel')).toHaveCount(0);
  });

  // -------------------------------------------------------------------------
  // Shipment lookup — tracking ID in mono font
  // -------------------------------------------------------------------------

  test('shipment_lookup tool output renders tracking ID in mono font', async ({ page }) => {
    await expect(page.getByTestId('logistics-panel')).toBeVisible();
    await page.waitForTimeout(200);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'shipment_lookup',
            tracking_id: 'SHP-20240312-AUH',
            origin: 'Shenzhen, China',
            destination: 'Abu Dhabi, UAE',
            status: 'in_transit',
            eta: '2024-03-18',
            carrier: 'Emirates SkyCargo',
            delay_days: 0,
            found: true,
          },
        })
      );
    });

    const card = page.getByTestId('logistics-shipment-card');
    await expect(card).toHaveCount(1);
    await expect(card).toHaveAttribute('data-found', 'true');

    // Tracking ID should be rendered in mono font element
    const trackingEl = page.getByTestId('shipment-tracking-id');
    await expect(trackingEl).toBeVisible();
    await expect(trackingEl).toContainText('SHP-20240312-AUH');
    const cls = await trackingEl.getAttribute('class');
    expect(cls).toContain('mono');
  });

  test('shipment_lookup with in_transit renders correct status badge', async ({ page }) => {
    await expect(page.getByTestId('logistics-panel')).toBeVisible();
    await page.waitForTimeout(200);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'shipment_lookup',
            tracking_id: 'SHP-20240312-AUH',
            status: 'in_transit',
            carrier: 'Emirates SkyCargo',
            eta: '2024-03-18',
            delay_days: 0,
            found: true,
          },
        })
      );
    });

    const badge = page.getByTestId('shipment-status-badge');
    await expect(badge).toHaveAttribute('data-status', 'in_transit');
    await expect(badge).toContainText('In Transit');
  });

  test('shipment_lookup with delayed status renders amber badge', async ({ page }) => {
    await expect(page.getByTestId('logistics-panel')).toBeVisible();
    await page.waitForTimeout(200);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'shipment_lookup',
            tracking_id: 'SHP-20240315-MXP',
            status: 'delayed',
            carrier: 'DHL Freight',
            eta: '2024-03-22',
            delay_days: 3,
            found: true,
          },
        })
      );
    });

    const badge = page.getByTestId('shipment-status-badge');
    await expect(badge).toHaveAttribute('data-status', 'delayed');
    const cls = await badge.getAttribute('class');
    expect(cls).toContain('amber');
  });

  test('shipment_lookup not found renders not-found message', async ({ page }) => {
    await expect(page.getByTestId('logistics-panel')).toBeVisible();
    await page.waitForTimeout(200);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: { type: 'shipment_lookup', found: false },
        })
      );
    });

    const card = page.getByTestId('logistics-shipment-card');
    await expect(card).toHaveAttribute('data-found', 'false');
    await expect(card).toContainText('not found');
  });

  // -------------------------------------------------------------------------
  // Delay flag card
  // -------------------------------------------------------------------------

  test('delay_flag tool output renders warning card', async ({ page }) => {
    await expect(page.getByTestId('logistics-panel')).toBeVisible();
    await page.waitForTimeout(200);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'delay_flag',
            tracking_id: 'SHP-20240310-AUH',
            reason: 'Certificate of origin under review at Abu Dhabi customs',
            confirmation: 'Delay flag published for SHP-20240310-AUH.',
          },
        })
      );
    });

    await expect(page.getByTestId('logistics-delay-flag-card')).toHaveCount(1);
    const card = page.getByTestId('logistics-delay-flag-card');
    await expect(card).toContainText('SHP-20240310-AUH');
    await expect(card).toContainText('Certificate of origin');
  });

  // -------------------------------------------------------------------------
  // Carrier brief card
  // -------------------------------------------------------------------------

  test('carrier_brief tool output renders metrics card', async ({ page }) => {
    await expect(page.getByTestId('logistics-panel')).toBeVisible();
    await page.waitForTimeout(200);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'carrier_brief',
            carrier: 'Emirates SkyCargo',
            on_time_rate_pct: 91.4,
            avg_delay_days: 0.8,
            open_incidents: 2,
            recommendation: 'Preferred carrier for UAE-origin air freight.',
            found: true,
          },
        })
      );
    });

    const card = page.getByTestId('logistics-carrier-card');
    await expect(card).toHaveCount(1);
    await expect(card).toHaveAttribute('data-found', 'true');
    await expect(card).toContainText('Emirates SkyCargo');
    await expect(card).toContainText('91.4');
    await expect(card).toContainText('Preferred carrier');
  });

  test('carrier_brief not found renders not-found message', async ({ page }) => {
    await expect(page.getByTestId('logistics-panel')).toBeVisible();
    await page.waitForTimeout(200);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: { type: 'carrier_brief', found: false },
        })
      );
    });

    const card = page.getByTestId('logistics-carrier-card');
    await expect(card).toHaveAttribute('data-found', 'false');
    await expect(card).toContainText('not found');
  });

  // -------------------------------------------------------------------------
  // Multiple outputs stack
  // -------------------------------------------------------------------------

  test('multiple tool outputs stack in LogisticsPanel', async ({ page }) => {
    await expect(page.getByTestId('logistics-panel')).toBeVisible();
    await page.waitForTimeout(200);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: { type: 'shipment_lookup', tracking_id: 'SHP-A', found: true, status: 'in_transit', carrier: 'Test', eta: '2024-04-01', delay_days: 0 },
        })
      );
    });
    await expect(page.getByTestId('logistics-shipment-card')).toHaveCount(1);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: { type: 'shipment_lookup', tracking_id: 'SHP-B', found: true, status: 'delayed', carrier: 'Test', eta: '2024-04-05', delay_days: 2 },
        })
      );
    });
    await expect(page.getByTestId('logistics-shipment-card')).toHaveCount(2);
  });

  // -------------------------------------------------------------------------
  // DemoGuidePanel
  // -------------------------------------------------------------------------

  test('DemoGuidePanel shows logistics scenarios', async ({ page }) => {
    const guidePanel = page.getByTestId('demo-guide-panel');
    await expect(guidePanel).toBeVisible();
    await expect(guidePanel).toContainText('Customs Hold');
  });
});
