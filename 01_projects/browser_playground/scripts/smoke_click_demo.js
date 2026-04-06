const fs = require("fs");
const path = require("path");
const { pathToFileURL } = require("url");
const { chromium } = require("playwright");

async function run() {
  const projectRoot = path.resolve(__dirname, "..");
  const demoPath = path.join(projectRoot, "demo_site", "index.html");
  const artifactDir = path.join(projectRoot, "artifacts");
  const screenshotPath = path.join(artifactDir, "smoke-click.png");
  const demoUrl = pathToFileURL(demoPath).href;

  fs.mkdirSync(artifactDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });

  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    await page.goto(demoUrl, { waitUntil: "load" });

    const statusBefore = await page.locator("#status-text").textContent();
    if (statusBefore !== "Waiting for click") {
      throw new Error(`Unexpected initial state: ${statusBefore}`);
    }

    await page.click("#demo-button");

    const statusAfter = await page.locator("#status-text").textContent();
    if (statusAfter !== "Click confirmed") {
      throw new Error(`Expected status to change, got: ${statusAfter}`);
    }

    const buttonState = await page.locator("#demo-button").getAttribute("data-clicked");
    if (buttonState !== "yes") {
      throw new Error("Button click marker was not applied.");
    }

    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`smoke_screenshot: ${screenshotPath}`);
  } finally {
    await browser.close();
  }
}

run().catch((error) => {
  console.error(`smoke_error: ${error.message}`);
  process.exit(1);
});
