/* Browser checks for the real Vite dev server; no mocked page content. */
const fs = require('node:fs/promises')
const path = require('node:path')
const assert = require('node:assert/strict')
const { chromium } = require('C:/Users/Magal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright')

const root = path.resolve(__dirname, '..')
const output = path.join(root, 'deliverables/lab09/evidence')
const base = 'http://localhost:5173'
const result = { base, browser: 'Microsoft Edge / Playwright', checks: [], errors: {} }
const check = (label, condition) => { assert.ok(condition, label); result.checks.push({ label, passed: true }) }

async function main() {
  await fs.mkdir(output, { recursive: true })
  const browser = await chromium.launch({ headless: true, executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe' })
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 })
    const cleanErrors = []
    page.on('console', (message) => { if (message.type() === 'error') cleanErrors.push(message.text()) })
    page.on('pageerror', (error) => cleanErrors.push(error.message))
    const response = await page.goto(base, { waitUntil: 'networkidle' })
    check('Vite responde por HTTP 200', response.status() === 200)
    check('Ocho tarjetas de película', await page.locator('.movie-list > li > article').count() === 8)
    check('Ocho clasificaciones', await page.locator('.movie-card__classification').count() === 8)
    check('Ocho sinopsis disponibles', await page.locator('.movie-card details').count() === 8)
    await page.locator('.footer').scrollIntoViewIfNeeded()
    check('Ocho imágenes locales cargadas', await page.locator('.movie-card img').evaluateAll((images) => images.length === 8 && images.every((image) => image.complete && image.naturalWidth > 0)))
    check('Ruta 91 muestra el caso sin funciones', (await page.locator('#pelicula-5').innerText()).includes('Sin funciones hoy'))
    check('Enlaces de navegación apuntan a secciones existentes', await page.locator('.header nav a').evaluateAll((links) => links.every((link) => document.querySelector(link.getAttribute('href')))))
    await page.locator('.hero a').click()
    check('Hero navega a horarios-1', new URL(page.url()).hash === '#horarios-1')
    await page.locator('#pelicula-1 summary').click()
    check('La sinopsis hostil permanece literal', (await page.locator('#pelicula-1 .synopsis').textContent()).includes('<img src=x onerror='))
    check('Sin imágenes ni script inyectados en sinopsis y agente', await page.locator('.synopsis img, .synopsis b, .synopsis script, .agent-message img, .agent-message b').count() === 0)
    check('window.__xss sin definir en la interfaz segura', await page.evaluate(() => typeof window.__xss === 'undefined'))
    await page.locator('#pelicula-1 summary').click()
    await page.goto(base, { waitUntil: 'networkidle' })
    await page.screenshot({ path: path.join(output, 'desktop.png') })
    await page.screenshot({ path: path.join(output, 'desktop-full.png'), fullPage: true })
    await page.locator('.billboard').screenshot({ path: path.join(output, 'movie-list.png') })
    await page.locator('.screenings').screenshot({ path: path.join(output, 'showtimes.png') })
    await page.locator('.editorial').screenshot({ path: path.join(output, 'untrusted-text.png') })
    await page.locator('.footer').screenshot({ path: path.join(output, 'footer.png') })
    for (const width of [320, 390, 768, 1024, 1440]) {
      await page.setViewportSize({ width, height: 900 })
      check(`Sin desbordamiento horizontal a ${width}px`, await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth))
      if (width === 390) { await page.goto(base, { waitUntil: 'networkidle' }); await page.screenshot({ path: path.join(output, 'mobile.png'), fullPage: true }) }
    }
    check('Cartelera sin errores de consola', cleanErrors.length === 0)
    result.consoleErrors = cleanErrors
    for (const example of ['class', 'key', 'roots']) {
      const examplePage = await browser.newPage({ viewport: { width: 1200, height: 780 } })
      const messages = []
      examplePage.on('console', (message) => { if (message.type() === 'error') messages.push(message.text()) })
      examplePage.on('pageerror', (error) => messages.push(error.message))
      await examplePage.goto(`${base}/lab-errors/?case=${example}`, { waitUntil: 'networkidle' })
      if (example === 'roots') await examplePage.locator('vite-error-overlay').waitFor()
      else await examplePage.locator(example === 'class' ? 'footer' : 'ul').waitFor()
      result.errors[example] = { messages }
      if (example === 'roots') result.errors[example].overlay = await examplePage.locator('vite-error-overlay').evaluate((element) => element.shadowRoot.textContent)
      await examplePage.screenshot({ path: path.join(output, `error-${example}.png`) })
      await examplePage.close()
    }
    check('Aviso real por class en JSX', result.errors.class.messages.some((message) => /Invalid DOM property.*class/.test(message)))
    check('Aviso real por key ausente', result.errors.key.messages.some((message) => /unique.*key/.test(message)))
    check('Error real por dos raíces JSX', /Adjacent JSX|Unexpected token|Expected/.test(result.errors.roots.overlay))
    const synopsisPath = path.join(root, 'frontend/src/components/Synopsis/Synopsis.jsx')
    const original = await fs.readFile(synopsisPath, 'utf8')
    const unsafePage = await browser.newPage({ viewport: { width: 1200, height: 900 } })
    try {
      await fs.writeFile(synopsisPath, original.replace('<p className="synopsis">{text}</p>', '<p className="synopsis" dangerouslySetInnerHTML={{ __html: text }} />'))
      await unsafePage.goto(base, { waitUntil: 'networkidle' })
      await unsafePage.waitForFunction(() => window.__xss === 1)
      result.unsafeExperiment = { flag: await unsafePage.evaluate(() => window.__xss), injectedImages: await unsafePage.locator('.synopsis img').count() }
      await unsafePage.locator('.editorial').screenshot({ path: path.join(output, 'unsafe-synopsis.png') })
    } finally {
      await fs.writeFile(synopsisPath, original)
      await unsafePage.close()
    }
    const restoredPage = await browser.newPage()
    await restoredPage.goto(base, { waitUntil: 'networkidle' })
    check('Experimento inseguro ejecutó únicamente la bandera local esperada', result.unsafeExperiment.flag === 1)
    check('Componente restaurado escapa etiquetas y no ejecuta código', await restoredPage.evaluate(() => typeof window.__xss === 'undefined' && document.querySelectorAll('.synopsis img').length === 0))
    result.restoredSource = true
    await restoredPage.close()
    await page.close()
  } finally { await browser.close() }
  await fs.writeFile(path.join(output, 'browser-results.json'), JSON.stringify(result, null, 2))
  console.log(`${result.checks.length} browser checks passed; three JSX errors recorded; unsafe experiment reverted.`)
}
main().catch((error) => { console.error(error); process.exitCode = 1 })
