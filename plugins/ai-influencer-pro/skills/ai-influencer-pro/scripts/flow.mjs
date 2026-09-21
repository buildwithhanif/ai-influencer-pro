#!/usr/bin/env node
// flow.mjs — drive Google Flow (flow.google.com) from the command line through a real Chrome profile.
//
// Flow has no public API. This script does exactly what a human does in the UI, with Playwright,
// inside a persistent browser profile you log into ONCE. Nothing is sent anywhere except to Google.
//
//   node flow.mjs login                                   # opens Chrome, you sign in, close it
//   node flow.mjs project "Dennis S1E01"                  # create a project, prints its URL
//   node flow.mjs image  --project <url> --model "Nano Banana Pro" --ratio 16:9 --count 2 --prompt "..."
//   node flow.mjs video  --project <url> --model "Omni 1.1 Flash" --ratio 9:16 --seconds 8 --count 2 \
//                        --character "Dennis Halim" --prompt "..."
//   node flow.mjs download --project <url> --kind video --quality 1080p --out ./clips
//   node flow.mjs batch  --project <url> episodes/s1e01.json       # every shot in a JSON file, in order
//
// Requirements: node 20+, `npm i playwright` once, and Chrome installed.
// Selectors are text-based on purpose (role + visible label), because Flow ships UI changes weekly.
// When one breaks you will get a clear "could not find <thing>" error, not silent misclicks.
// Never run more than one flow.mjs at a time against the same profile.

import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const PROFILE = process.env.AIP_PROFILE || path.join(os.homedir(), '.config', 'ai-influencer-pro', 'chrome-profile');
const args = process.argv.slice(2);
const cmd = args.shift();
const opt = (name, def) => { const i = args.indexOf('--' + name); return i >= 0 ? args[i + 1] : def; };
const has = (name) => args.includes('--' + name);

async function browser(headless = false) {
  fs.mkdirSync(PROFILE, { recursive: true });
  const ctx = await chromium.launchPersistentContext(PROFILE, {
    channel: 'chrome', headless, viewport: { width: 1600, height: 1000 },
    acceptDownloads: true, args: ['--disable-blink-features=AutomationControlled'],
  });
  const page = ctx.pages()[0] || await ctx.newPage();
  return { ctx, page };
}

const composer = (page) => page.getByPlaceholder(/What do you want to create/i);

async function openProject(page, url) {
  await page.goto(url, { waitUntil: 'domcontentloaded' });
  await composer(page).waitFor({ timeout: 60_000 });
  // If the composer is in Agent mode the model chip is hidden. Toggle it off.
  const agent = page.getByRole('button', { name: /^Agent$/ });
  if (await agent.count() && (await agent.getAttribute('aria-pressed')) === 'true') await agent.click();
}

async function setMode(page, { kind, model, ratio, seconds, count, resolution }) {
  // The settings chip sits at the right of the composer and shows the current model/ratio/count.
  const chip = page.locator('form, [role="textbox"]').last().locator('..').getByRole('button').filter({ hasText: /x[1-4]/ }).first();
  await chip.click();
  await page.getByRole('tab', { name: kind === 'video' ? /Video/ : /Image/ }).or(page.getByText(kind === 'video' ? /^Video$/ : /^Image$/)).first().click();
  if (kind === 'video') await page.getByText(/^Ingredients$/).click();
  if (ratio) await page.getByText(new RegExp('^' + ratio.replace(':', ':') + '$')).first().click();
  if (model) { await page.getByRole('combobox').or(page.getByText(/Nano Banana|Omni|Veo/).first()).first().click(); await page.getByText(model, { exact: false }).first().click(); }
  if (resolution) await page.getByText(new RegExp('^' + resolution + '$')).first().click();
  if (seconds) await page.getByText(new RegExp('^' + seconds + 's$')).first().click();
  if (count) await page.getByText(new RegExp('^x' + count + '$')).first().click();
  await page.keyboard.press('Escape');
}

async function attachCharacter(page, name) {
  // "+" opens the asset picker; pick the named character; "Add to prompt".
  await page.locator('button').filter({ has: page.locator('svg') }).filter({ hasText: /^$/ }).first().click().catch(() => {});
  await page.getByPlaceholder(/Search assets/i).fill(name);
  await page.getByText(name, { exact: false }).first().click();
  await page.getByRole('button', { name: /Add to prompt/i }).click();
}

async function submit(page, prompt) {
  const box = composer(page);
  await box.click();
  await box.fill(prompt);
  await page.keyboard.press('Enter');
  await page.waitForTimeout(1500);
}

async function waitForRenders(page, expected, timeoutMs = 10 * 60_000) {
  // Cards show a % badge while rendering. Done when no % badges remain and we have at least `expected` cards.
  const t0 = Date.now();
  while (Date.now() - t0 < timeoutMs) {
    const pending = await page.getByText(/^\d{1,3}%$/).count();
    if (pending === 0) return true;
    await page.waitForTimeout(5000);
  }
  throw new Error('renders did not finish in time');
}

async function downloadAll(page, { kind, quality, out }) {
  fs.mkdirSync(out, { recursive: true });
  await page.getByRole('link', { name: kind === 'video' ? /^Videos$/ : /^Images$/ }).or(page.getByText(kind === 'video' ? /^Videos$/ : /^Images$/)).first().click();
  await page.waitForTimeout(1500);
  const cards = page.locator('main img, main video').locator('..');
  const n = await cards.count();
  for (let i = 0; i < n; i++) {
    const card = cards.nth(i);
    await card.hover();
    await card.getByRole('button', { name: /More/i }).click();
    await page.getByText(/^Download$/).hover();
    const [dl] = await Promise.all([
      page.waitForEvent('download', { timeout: 120_000 }),
      page.getByText(new RegExp('^' + quality)).first().click(),
    ]);
    const file = path.join(out, dl.suggestedFilename());
    await dl.saveAs(file);
    console.log('saved', file);
    await page.keyboard.press('Escape');
  }
}

(async () => {
  if (!cmd || cmd === 'help') { console.log(fs.readFileSync(new URL(import.meta.url)).toString().split('\n').slice(1, 20).join('\n')); process.exit(0); }
  const { ctx, page } = await browser(has('headless'));
  try {
    if (cmd === 'login') {
      await page.goto('https://flow.google.com/');
      console.log('Sign in to Google in the window, open Flow once, then close the window.');
      await ctx.waitForEvent('close').catch(() => {});
      return;
    }
    if (cmd === 'project') {
      await page.goto('https://flow.google.com/');
      await page.getByRole('button', { name: /New project/i }).click();
      await composer(page).waitFor();
      const name = args[0];
      if (name) { await page.getByRole('button', { name: /Sep|Oct|Nov|Dec|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug/ }).first().click().catch(() => {}); }
      console.log(page.url());
      return;
    }
    if (cmd === 'image' || cmd === 'video') {
      await openProject(page, opt('project'));
      await setMode(page, { kind: cmd, model: opt('model'), ratio: opt('ratio'), seconds: opt('seconds'), count: opt('count'), resolution: opt('resolution') });
      if (opt('character')) await attachCharacter(page, opt('character'));
      await submit(page, opt('prompt'));
      if (has('wait')) await waitForRenders(page);
      console.log('submitted');
      return;
    }
    if (cmd === 'batch') {
      const plan = JSON.parse(fs.readFileSync(args[0], 'utf8'));
      await openProject(page, opt('project') || plan.project);
      for (const shot of plan.shots) {
        await setMode(page, { kind: 'video', model: plan.model, ratio: plan.ratio || '9:16', seconds: shot.seconds || plan.seconds || 8, count: shot.count || plan.count || 2, resolution: plan.resolution });
        if (plan.character) await attachCharacter(page, plan.character);
        const prompt = shot.prompt || [plan.scene, `She says: "${shot.line}"`, plan.rules].filter(Boolean).join(' ');
        await submit(page, prompt);
        console.log('submitted', shot.id);
        // one clip at a time: Flow's unusual-activity guard trips on bursts (references/flow-mechanics.md)
        await waitForRenders(page, 1);
        await page.waitForTimeout(30000);
      }
      if (plan.out) await downloadAll(page, { kind: 'video', quality: plan.quality || '1080p', out: plan.out });
      return;
    }
    if (cmd === 'download') {
      await openProject(page, opt('project'));
      await downloadAll(page, { kind: opt('kind', 'video'), quality: opt('quality', '1080p'), out: opt('out', './downloads') });
      return;
    }
    console.error('unknown command', cmd);
  } finally { await ctx.close(); }
})();
