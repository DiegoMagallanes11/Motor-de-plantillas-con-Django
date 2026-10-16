/* Optional browser evidence helper for the Codex workspace runtime. */
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('C:/Users/Magal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

(async () => {
  const output = path.resolve(__dirname, '..', 'deliverables', 'lab07', 'evidence');
  fs.mkdirSync(output, {recursive:true});
  const browser = await chromium.launch({
    executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    headless:true,
  });
  const page = await browser.newPage({viewport:{width:1440,height:1100},locale:'es-PE'});
  const errors = [];
  page.on('pageerror', error=>errors.push(error.message));
  const response = await page.goto(
    process.env.LAB07_URL || 'http://127.0.0.1:8004/laboratorio-7/',
    {waitUntil:'networkidle'}
  );
  if (response.status() !== 200) throw new Error('Dashboard did not load');
  const accepted = await page.locator('.duel-table .accepted').count();
  if (accepted !== 8) throw new Error('Expected eight accepted reference queries');
  const statuses = await page.locator('.intents-grid .status').allTextContents();
  if (JSON.stringify(statuses) !== JSON.stringify(['ok','ok','approval_required','denied'])) throw new Error('Unexpected intent statuses');
  if (!await page.locator('blockquote').innerText().then(text=>text.includes('execute_sql'))) throw new Error('Missing untrusted comment');
  const schemaLoaded = await page.locator('.schema-image').evaluate(image=>image.complete && image.naturalWidth > 0);
  if (!schemaLoaded) throw new Error('Relationship diagram did not load');
  await page.screenshot({path:path.join(output,'04-dashboard.png'),fullPage:true});
  await page.locator('#data').screenshot({path:path.join(output,'05-data-relations.png')});
  await page.locator('#queries').screenshot({path:path.join(output,'06-duel.png')});
  await page.locator('#performance').screenshot({path:path.join(output,'07-n-plus-one.png')});
  await page.locator('#actions').screenshot({path:path.join(output,'08-agent.png')});
  await page.locator('.duel-table tbody tr').nth(4).locator('summary').click();
  if (!await page.locator('.duel-table tbody tr').nth(4).locator('pre').first().isVisible()) throw new Error('Query SQL details did not expand');
  await page.locator('.duel-table tbody tr').nth(4).screenshot({path:path.join(output,'09-counts-detail.png')});
  await page.setViewportSize({width:390,height:844});
  await page.goto(process.env.LAB07_URL || 'http://127.0.0.1:8004/laboratorio-7/',{waitUntil:'networkidle'});
  if (await page.evaluate(()=>document.documentElement.scrollWidth > innerWidth)) throw new Error('Horizontal viewport overflow');
  await page.screenshot({path:path.join(output,'10-mobile.png'),fullPage:true});
  const home = new URL('/',page.url()).href;
  await page.goto(home,{waitUntil:'networkidle'});
  if (await page.locator('.article-card').count() !== 6) throw new Error('Lab 06 was not preserved');
  if (errors.length) throw new Error(errors.join('\n'));
  fs.writeFileSync(path.join(output,'browser-results.json'),JSON.stringify({
    status:'passed',referenceAccepted:accepted,intentStatuses:statuses,
    schemaLoaded,sqlDetailsExpanded:true,mobileOverflow:false,
    lab06Cards:6,pageErrors:errors,
  },null,2));
  await browser.close();
  console.log('Lab 07 browser checks passed; Lab 06 preserved.');
})().catch(error=>{console.error(error.message);process.exit(1);});
