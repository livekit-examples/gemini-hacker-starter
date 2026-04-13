import { test, expect } from '@playwright/test';

test.describe('Manufacturing Demo — Session 17', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/demo/manufacturing');
    await page.waitForSelector('[data-testid="dashboard-layout"]', { timeout: 10_000 });
  });

  // -------------------------------------------------------------------------
  // Basic page load
  // -------------------------------------------------------------------------

  test('/demo/manufacturing loads without error', async ({ page }) => {
    await expect(page).toHaveURL('/demo/manufacturing');
    await expect(page.getByTestId('dashboard-layout')).toBeVisible();
  });

  // -------------------------------------------------------------------------
  // PersonaCard — Marco
  // -------------------------------------------------------------------------

  test('PersonaCard shows "Marco"', async ({ page }) => {
    await expect(page.getByTestId('persona-name')).toContainText('Marco');
  });

  test('PersonaCard shows "Process & Quality Engineer" role', async ({ page }) => {
    await expect(page.getByTestId('persona-role')).toContainText('Quality Engineer');
  });

  test('PersonaCard shows initials "MA"', async ({ page }) => {
    await expect(page.getByTestId('persona-initials')).toContainText('MA');
  });

  // -------------------------------------------------------------------------
  // ManufacturingPanel is present
  // -------------------------------------------------------------------------

  test('ManufacturingPanel is rendered instead of generic ToolOutputPanel', async ({ page }) => {
    await expect(page.getByTestId('manufacturing-panel')).toBeVisible();
    await expect(page.getByTestId('tool-output-panel')).toHaveCount(0);
  });

  // -------------------------------------------------------------------------
  // defect_detection tool output → DefectDetectionCard
  // -------------------------------------------------------------------------

  test('defect_detection tool output renders DefectDetectionCard with severity badge', async ({ page }) => {
    await expect(page.getByTestId('manufacturing-panel')).toBeVisible();
    await page.waitForTimeout(200);
    await expect(page.getByTestId('manufacturing-defect-card')).toHaveCount(0);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'defect_detection',
            defect_type: 'structural_crack',
            severity: 'critical',
            area: 'load-bearing bracket',
            recommended_action: 'Remove part from line immediately. Do not rework. Tag with NCR and quarantine.',
          },
        })
      );
    });

    await expect(page.getByTestId('manufacturing-defect-card')).toHaveCount(1);
    const card = page.getByTestId('manufacturing-defect-card');
    await expect(card).toContainText('Structural Crack');
    await expect(card).toContainText('load-bearing bracket');
    await expect(card).toContainText('NCR');
  });

  test('critical severity badge has red colour class', async ({ page }) => {
    await expect(page.getByTestId('manufacturing-panel')).toBeVisible();
    await page.waitForTimeout(200);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'defect_detection',
            defect_type: 'structural_crack',
            severity: 'critical',
            area: 'bracket',
            recommended_action: 'Stop production.',
          },
        })
      );
    });

    const badge = page.getByTestId('severity-badge');
    await expect(badge).toHaveAttribute('data-severity', 'critical');
    await expect(badge).toContainText('critical');
    const cls = await badge.getAttribute('class');
    expect(cls).toContain('red');
  });

  test('major severity badge has amber colour class', async ({ page }) => {
    await expect(page.getByTestId('manufacturing-panel')).toBeVisible();
    await page.waitForTimeout(200);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'defect_detection',
            defect_type: 'weld_porosity',
            severity: 'major',
            area: 'weld bead',
            recommended_action: 'Grind and re-weld.',
          },
        })
      );
    });

    const badge = page.getByTestId('severity-badge');
    await expect(badge).toHaveAttribute('data-severity', 'major');
    const cls = await badge.getAttribute('class');
    expect(cls).toContain('amber');
  });

  test('minor severity badge has green colour class', async ({ page }) => {
    await expect(page.getByTestId('manufacturing-panel')).toBeVisible();
    await page.waitForTimeout(200);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'defect_detection',
            defect_type: 'burr_or_sharp_edge',
            severity: 'minor',
            area: 'drilled hole edge',
            recommended_action: 'Deburr and re-inspect.',
          },
        })
      );
    });

    const badge = page.getByTestId('severity-badge');
    await expect(badge).toHaveAttribute('data-severity', 'minor');
    const cls = await badge.getAttribute('class');
    expect(cls).toContain('green');
  });

  // -------------------------------------------------------------------------
  // sop_lookup tool output → SopLookupCard with numbered steps
  // -------------------------------------------------------------------------

  test('sop_lookup tool output renders numbered steps list', async ({ page }) => {
    await expect(page.getByTestId('manufacturing-panel')).toBeVisible();
    await page.waitForTimeout(200);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'sop_lookup',
            procedure_id: 'SOP-MFG-002',
            title: 'Lockout/Tagout (LOTO) — CNC Milling Machine LM-400',
            steps: [
              'Notify all affected employees before initiating LOTO on LM-400.',
              'Power down the machine using the main control panel.',
              'Apply your personal lock to the hasp on the disconnect.',
            ],
            found: true,
          },
        })
      );
    });

    const card = page.getByTestId('manufacturing-sop-card');
    await expect(card).toHaveCount(1);
    await expect(card).toHaveAttribute('data-found', 'true');
    await expect(card).toContainText('Lockout/Tagout');

    // Numbered steps list should be present
    const stepsList = page.getByTestId('sop-steps-list');
    await expect(stepsList).toBeVisible();
    await expect(stepsList).toContainText('Notify all affected employees');
  });

  test('sop_lookup with found=false renders not-found message', async ({ page }) => {
    await expect(page.getByTestId('manufacturing-panel')).toBeVisible();
    await page.waitForTimeout(200);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'sop_lookup',
            procedure_id: '',
            title: '',
            steps: [],
            found: false,
          },
        })
      );
    });

    const card = page.getByTestId('manufacturing-sop-card');
    await expect(card).toHaveAttribute('data-found', 'false');
    await expect(card).toContainText('No matching procedure found');
  });

  // -------------------------------------------------------------------------
  // defect_report tool output → DefectReportCard
  // -------------------------------------------------------------------------

  test('defect_report tool output renders report card', async ({ page }) => {
    await expect(page.getByTestId('manufacturing-panel')).toBeVisible();
    await page.waitForTimeout(200);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'defect_report',
            report: 'DEFECT REPORT\n========================================\nDefect #1  [CRITICAL]\n  Type  : structural_crack\n  Area  : load-bearing bracket\n  Action: Quarantine immediately.',
            defect_count: 1,
          },
        })
      );
    });

    await expect(page.getByTestId('manufacturing-defect-report-card')).toHaveCount(1);
    const card = page.getByTestId('manufacturing-defect-report-card');
    await expect(card).toContainText('DEFECT REPORT');
    await expect(card).toContainText('structural_crack');
  });

  // -------------------------------------------------------------------------
  // Multiple tool outputs stack
  // -------------------------------------------------------------------------

  test('multiple tool outputs stack in ManufacturingPanel', async ({ page }) => {
    await expect(page.getByTestId('manufacturing-panel')).toBeVisible();
    await page.waitForTimeout(200);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'defect_detection',
            defect_type: 'structural_crack',
            severity: 'critical',
            area: 'bracket',
            recommended_action: 'Stop.',
          },
        })
      );
    });
    await expect(page.getByTestId('manufacturing-defect-card')).toHaveCount(1);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'defect_detection',
            defect_type: 'surface_scratch',
            severity: 'minor',
            area: 'panel',
            recommended_action: 'Polish.',
          },
        })
      );
    });
    await expect(page.getByTestId('manufacturing-defect-card')).toHaveCount(2);
  });

  // -------------------------------------------------------------------------
  // DemoGuidePanel shows manufacturing scenarios
  // -------------------------------------------------------------------------

  test('DemoGuidePanel shows manufacturing scenarios', async ({ page }) => {
    const guidePanel = page.getByTestId('demo-guide-panel');
    await expect(guidePanel).toBeVisible();
    await expect(guidePanel).toContainText('Weld Defect');
  });
});
