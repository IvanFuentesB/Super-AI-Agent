const fs = require("fs");
const path = require("path");
const { pathToFileURL } = require("url");
const { chromium } = require("playwright");

function getArgValue(flag) {
  const index = process.argv.indexOf(flag);
  if (index === -1 || index === process.argv.length - 1) {
    return null;
  }

  return process.argv[index + 1];
}

function parsePositiveInteger(value, fallbackValue) {
  const parsed = Number.parseInt(value, 10);
  if (Number.isNaN(parsed) || parsed < 0) {
    return fallbackValue;
  }

  return parsed;
}

function resolveOptions() {
  const envMode = (process.env.BROWSER_PLAYGROUND_MODE || "").toLowerCase();
  const visible = process.argv.includes("--visible") ||
    envMode === "visible" ||
    process.env.BROWSER_PLAYGROUND_VISIBLE === "1";
  const checkOnly = process.argv.includes("--check-only");
  const slowMo = visible
    ? parsePositiveInteger(
        getArgValue("--slow-mo") || process.env.BROWSER_PLAYGROUND_SLOW_MO,
        250,
      )
    : 0;
  const keepOpenMs = visible
    ? parsePositiveInteger(
        getArgValue("--keep-open-ms") || process.env.BROWSER_PLAYGROUND_KEEP_OPEN_MS,
        2000,
      )
    : 0;

  return {
    visible,
    checkOnly,
    slowMo,
    keepOpenMs,
  };
}

async function run() {
  const projectRoot = path.resolve(__dirname, "..");
  const demoPath = path.join(projectRoot, "demo_site", "index.html");
  const artifactDir = path.join(projectRoot, "artifacts");
  const screenshotPath = path.join(artifactDir, "smoke-click.png");
  const demoUrl = pathToFileURL(demoPath).href;
  const options = resolveOptions();

  fs.mkdirSync(artifactDir, { recursive: true });

  if (options.checkOnly) {
    console.log(`mode: ${options.visible ? "visible" : "smoke"}`);
    console.log(`headless: ${options.visible ? "no" : "yes"}`);
    console.log(`slow_mo: ${options.slowMo}`);
    console.log(`keep_open_ms: ${options.keepOpenMs}`);
    console.log(`demo_url: ${demoUrl}`);
    console.log(`screenshot_path: ${screenshotPath}`);
    return;
  }

  const browser = await chromium.launch({
    headless: !options.visible,
    slowMo: options.slowMo,
  });

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
    if (options.visible && options.keepOpenMs > 0) {
      await page.waitForTimeout(options.keepOpenMs);
    }
    console.log(`mode: ${options.visible ? "visible" : "smoke"}`);
    console.log(`smoke_screenshot: ${screenshotPath}`);
  } finally {
    await browser.close();
  }
}

run().catch((error) => {
  console.error(`smoke_error: ${error.message}`);
  process.exit(1);
});
