# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: onboarding.setup.ts >> first-run onboarding — wizard renders; "Set up later" lands in the cockpit
- Location: e2e/onboarding.setup.ts:8:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByRole('button', { name: 'Set up later' })
Expected: visible
Timeout: 15000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" getByRole('button', { name: 'Set up later' }) with timeout 15000ms
  - waiting for getByRole('button', { name: 'Set up later' })

```

```yaml
- main:
  - text: Pod by Coffee 1 of 6
  - strong: Private
  - progressbar
  - text: Welcome to Pod
  - heading "Private. Owned by you. Built to stay." [level=2]
  - paragraph: Pod lives on your machine. The agents you choose can read and write through MCP. Nothing else is connected.
  - article:
    - strong: Local
    - text: Lives on this Mac.
  - article:
    - strong: Bounded
    - text: One revocable key per agent.
  - article:
    - strong: Yours
    - text: Your memory stays with you.
  - button "Skip for now"
  - button "Set up my Pod"
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | /**
  4  |  * First-run journey (setup project). A fresh Pod shows the onboarding wizard;
  5  |  * "Set up later" completes setup and lands in the cockpit. Every other project
  6  |  * depends on this one, so the rest of the suite starts from an onboarded Pod.
  7  |  */
  8  | test('first-run onboarding — wizard renders; "Set up later" lands in the cockpit', async ({ page }) => {
  9  |   await page.goto('/');
  10 | 
  11 |   // Wizard, step 1 of 6
  12 |   await expect(page.getByText('One place for your memories to live and grow.')).toBeVisible();
  13 |   await expect(page.getByText('1 OF 6')).toBeVisible();
  14 |   const skip = page.getByRole('button', { name: 'Set up later' });
> 15 |   await expect(skip).toBeVisible();
     |                      ^ Error: expect(locator).toBeVisible() failed
  16 | 
  17 |   await skip.click();
  18 | 
  19 |   // Cockpit shell: sidebar nav, pod identity, first surface content
  20 |   await expect(page.locator('[data-nav="activity"]')).toBeVisible();
  21 |   await expect(page.getByText('E2E Pod').first()).toBeVisible();
  22 |   await expect(page.getByText('Give Pod something to remember')).toBeVisible();
  23 | });
  24 | 
```