import { expect, test } from "@playwright/test";

// Smoke test for the Phase 0 flow: an unauthenticated visitor is redirected
// to /login, and the login form is usable on a mobile viewport. Requires the
// API to be running (see docker-compose) — full register→login→dashboard
// coverage lands once there's a disposable test database to run against in CI.
test("unauthenticated visitor is redirected to the login page", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByRole("heading", { name: "Log in" })).toBeVisible();
  await expect(page.getByLabel(/email/i)).toBeVisible();
  await expect(page.getByLabel(/password/i)).toBeVisible();
});

test("login page links to registration", async ({ page }) => {
  await page.goto("/login");
  await page.getByRole("link", { name: /register/i }).click();
  await expect(page).toHaveURL(/\/register$/);
  await expect(page.getByRole("heading", { name: /create your account/i })).toBeVisible();
});
