import { test, expect } from '@playwright/test';

/** Wait for the ComunePanel to be fully mounted (event listeners registered). */
async function waitForPanelReady(page: Parameters<typeof test>[1]['page']) {
  await expect(page.getByTestId('tool-output-panel')).toBeVisible();
  // Wait for the empty-state placeholder — confirms event listeners are registered
  await expect(page.getByText('Service lookups will appear here.')).toBeVisible();
}

test.describe('Comune Demo Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/demo/comune');
    await page.waitForSelector('[data-testid="dashboard-layout"]', { timeout: 10_000 });
  });

  test('/demo/comune loads without error', async ({ page }) => {
    await expect(page.getByTestId('dashboard-layout')).toBeVisible();
  });

  test('PersonaCard shows "Giulia"', async ({ page }) => {
    await expect(page.getByTestId('persona-name')).toContainText('Giulia');
  });

  test('service_requirements tool-output renders a checklist', async ({ page }) => {
    await waitForPanelReady(page);

    // Simulate a service_requirements tool output
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'service_requirements',
            service: 'Iscrizione Anagrafe',
            service_id: 'ANA-001',
            required_documents: [
              'Documento di identità valido',
              'Codice fiscale',
              'Permesso di soggiorno',
            ],
            processing_days: 30,
            fee_eur: 0.0,
            office: 'Ufficio Anagrafe',
            bookable_online: true,
            notes: 'Portare originali e fotocopie',
            found: true,
          },
        })
      );
    });

    // Service requirements card should appear with checklist
    await expect(page.getByTestId('service-requirements-card')).toBeVisible();

    // Verify checklist items are rendered
    const items = page.locator('[data-testid="service-requirements-card"] ol li');
    await expect(items).toHaveCount(3);

    // Verify processing badge and fee badge
    await expect(page.getByTestId('processing-days-badge')).toBeVisible();
    await expect(page.getByTestId('fee-badge')).toBeVisible();

    // Verify office tag
    await expect(page.getByTestId('office-tag')).toContainText('Ufficio Anagrafe');
  });

  test('application_status tool-output renders status badge with correct colour', async ({
    page,
  }) => {
    await waitForPanelReady(page);

    // Simulate an approved application status
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'application_status',
            application_id: 'APP-2024-ANA-00341',
            service: 'Iscrizione Anagrafe',
            status: 'approved',
            submitted_on: '2024-09-01',
            expected_by: '2024-10-01',
            notes: 'Pratica approvata.',
            found: true,
          },
        })
      );
    });

    // Application status card should appear
    await expect(page.getByTestId('application-status-card')).toBeVisible();

    // Application ID rendered
    await expect(page.getByTestId('application-id')).toContainText('APP-2024-ANA-00341');

    // Status badge rendered with green class
    const badge = page.getByTestId('status-badge');
    await expect(badge).toBeVisible();
    await expect(badge).toContainText('Approved');
    const badgeClass = await badge.getAttribute('class');
    expect(badgeClass).toContain('green');
  });

  test('application_status with rejected status renders red badge', async ({ page }) => {
    await waitForPanelReady(page);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'application_status',
            application_id: 'APP-2024-PER-00031',
            service: 'Dehors — Outdoor Seating',
            status: 'rejected',
            submitted_on: '2024-07-15',
            expected_by: '2024-08-15',
            notes: 'Richiesta non conforme al regolamento.',
            found: true,
          },
        })
      );
    });

    const badge = page.getByTestId('status-badge');
    await expect(badge).toBeVisible();
    await expect(badge).toContainText('Rejected');
    const badgeClass = await badge.getAttribute('class');
    expect(badgeClass).toContain('red');
  });

  test('appointment_confirmation tool-output renders confirmation ID in mono font', async ({
    page,
  }) => {
    await waitForPanelReady(page);

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'appointment_confirmation',
            confirmation_id: 'APT-20250315-XK9M2R',
            service: 'Iscrizione Anagrafe',
            citizen_name: 'Fatima Al-Rashidi',
            date: '2025-03-17',
            time: '09:30',
            office: 'Ufficio Anagrafe — Piano 1',
            instructions:
              'Presentarsi con tutti i documenti richiesti. Cancellare almeno 24 ore prima.',
            found: true,
          },
        })
      );
    });

    // Appointment confirmation card should appear
    await expect(page.getByTestId('appointment-confirmation-card')).toBeVisible();

    // Confirmation ID should be rendered in mono font
    const confirmationId = page.getByTestId('confirmation-id');
    await expect(confirmationId).toBeVisible();
    await expect(confirmationId).toContainText('APT-20250315-XK9M2R');

    // Verify it uses font-mono class
    const fontClass = await confirmationId.getAttribute('class');
    expect(fontClass).toContain('font-mono');
  });

  test('multiple tool outputs stack in panel', async ({ page }) => {
    await waitForPanelReady(page);

    // Inject service_requirements first, then application_status
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'service_requirements',
            service: "Carta d'Identità",
            service_id: 'ANA-002',
            required_documents: ['Passaporto scaduto o deteriorato'],
            processing_days: 7,
            fee_eur: 22.0,
            office: 'Ufficio Anagrafe',
            bookable_online: true,
            notes: '',
            found: true,
          },
        })
      );
    });

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('__tool_output__', {
          detail: {
            type: 'application_status',
            application_id: 'APP-2024-SOC-00389',
            service: 'ISEE Declaration Assistance',
            status: 'pending',
            submitted_on: '2024-10-01',
            expected_by: '2024-11-15',
            notes: 'In lavorazione.',
            found: true,
          },
        })
      );
    });

    // Both cards should be visible
    await expect(page.getByTestId('service-requirements-card')).toBeVisible();
    await expect(page.getByTestId('application-status-card')).toBeVisible();
  });
});
