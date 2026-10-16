/* Capture real browser evidence against the running local development server. */
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('C:/Users/Magal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

(async () => {
  const root = path.resolve(__dirname, '..');
  const output = path.join(root, 'deliverables', 'evidence');
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    headless: true,
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1050 }, locale: 'es-PE' });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const base = process.env.PORTAL_URL || 'http://127.0.0.1:8000';
  async function capture(file) {
    await page.screenshot({ path: path.join(output, file), fullPage: true });
  }
  await page.goto(base, { waitUntil: 'networkidle' });
  if (await page.locator('.article-card').count() !== 6) throw new Error('Expected six news cards');
  if (!await page.locator('.brand').isVisible()) throw new Error('Missing site header');
  const images = await page.locator('.card-image img').evaluateAll(nodes => nodes.map(node => ({loaded: node.complete && node.naturalWidth > 0})));
  if (images.some(item => !item.loaded)) throw new Error('Image did not load');
  const background = await page.locator('body').evaluate(node => getComputedStyle(node).backgroundColor);
  if (background !== 'rgb(247, 246, 242)') throw new Error('Stylesheet did not load');
  await capture('01-home.png');
  await page.getByRole('navigation').getByRole('link', { name: 'Tecnología', exact: true }).click();
  if (await page.locator('.article-card').count() !== 2) throw new Error('Category should contain two articles');
  await capture('02-category.png');
  await page.getByRole('heading', {name: 'Diseñar herramientas que todos puedan usar'}).getByRole('link').click();
  const bodyText = await page.locator('.article-body').innerText();
  if (!bodyText.includes('<strong>Texto de prueba</strong>')) throw new Error('Escaped HTML missing');
  if (await page.locator('.article-body strong').count()) throw new Error('Stored HTML was executed');
  await capture('03-detail-escape.png');
  await page.setViewportSize({width:390,height:844});
  await page.goto(base, {waitUntil:'networkidle'});
  if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)) throw new Error('Mobile horizontal overflow');
  await capture('04-mobile.png');
  await page.setViewportSize({width:1440,height:1050});
  await page.goto(base + '/admin/login/', {waitUntil:'networkidle'});
  const credentials = fs.readFileSync(path.join(root,'.private','admin-access.txt'),'utf8');
  const password = credentials.match(/Contraseña: (.+)/)[1].trim();
  await page.locator('#id_username').fill('diego');
  await page.locator('#id_password').fill(password);
  await page.locator('input[type=submit]').click();
  await page.waitForURL(base + '/admin/');
  await capture('05-admin.png');
  await page.goto(base + '/admin/news/article/', {waitUntil:'networkidle'});
  await capture('06-admin-articles.png');
  await page.locator('#searchbar').fill('Diseñar herramientas');
  await page.locator('#changelist-search input[type=submit]').click();
  if (await page.locator('#result_list tbody tr').count() !== 1) throw new Error('Admin search failed');
  await capture('07-admin-search.png');
  await page.getByRole('link',{name:'Diseñar herramientas que todos puedan usar',exact:true}).click();
  await capture('08-admin-edit.png');
  const summary = await page.locator('#id_summary').inputValue();
  const marker = ' Actualización verificada desde el administrador.';
  await page.locator('#id_summary').fill(summary + marker);
  await page.locator('input[name=_save]').click();
  await page.goto(base + '/noticias/herramientas-accesibles/',{waitUntil:'networkidle'});
  if (!await page.locator('.article-summary').innerText().then(text=>text.includes(marker.trim()))) throw new Error('Admin change not visible');
  await capture('09-admin-change-visible.png');
  await page.goto(base + '/admin/news/article/',{waitUntil:'networkidle'});
  await page.getByRole('link',{name:'Diseñar herramientas que todos puedan usar',exact:true}).click();
  await page.locator('#id_summary').fill(summary);
  await page.locator('input[name=_save]').click();
  if (errors.length) throw new Error(errors.join('\n'));
  fs.writeFileSync(path.join(output,'browser-results.json'), JSON.stringify({status:'passed',cards:6,categoryCards:2,imagesLoaded:true,stylesheetLoaded:true,escapedHtml:true,mobileOverflow:false,adminSearch:true,adminEditVisible:true,pageErrors:errors},null,2));
  await browser.close();
  console.log('Browser verification passed; evidence saved.');
})().catch(error=>{console.error(error.message);process.exit(1);});
