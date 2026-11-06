/* Real DRF browsable API operations; tokens stay in the local private file. */
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('C:/Users/Magal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
  const out = path.resolve('deliverables/lab08/evidence');
  const token = JSON.parse(fs.readFileSync('.private/quiz_tokens.json','utf8')).human;
  const browser = await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true});
  const page = await browser.newPage({viewport:{width:1440,height:1050},extraHTTPHeaders:{Authorization:'Token '+token}});
  const base = 'http://127.0.0.1:8008';
  const steps = [];
  for(const resource of ['','exams/','questions/','choices/']){
    const response = await page.goto(base+'/api/'+resource,{waitUntil:'networkidle'});
    if(response.status()!==200)throw new Error('Browsable resource failed');
    await page.screenshot({path:path.join(out,'browser-'+(resource.replace('/','')||'root')+'.png'),fullPage:true});
  }
  let response = await page.goto(base+'/api/exams/',{waitUntil:'networkidle'});
  steps.push({operation:'list',status:response.status()});
  await page.locator('input[name=title]').fill('Prueba API navegable Lab08');
  [response] = await Promise.all([page.waitForResponse(r=>r.request().method()==='POST'&&r.url()===base+'/api/exams/'),page.getByRole('button',{name:'POST',exact:true}).click()]);
  if(response.status()!==201)throw new Error('UI POST failed '+response.status());
  steps.push({operation:'create',status:201});
  await page.waitForLoadState('networkidle');
  await page.screenshot({path:path.join(out,'browser-created-201.png'),fullPage:true});
  const text = (await page.locator('pre').allTextContents()).join('\n');
  const id = Number(text.match(/"id":\s*(\d+)/)[1]);
  fs.writeFileSync('.private/ui-lab08-target.json',JSON.stringify({id}));
  response = await page.goto(base+'/api/exams/'+id+'/',{waitUntil:'networkidle'});
  steps.push({operation:'retrieve',status:response.status()});
  await page.screenshot({path:path.join(out,'browser-detail-200.png'),fullPage:true});
  fs.writeFileSync('.private/ui-lab08-state.json',JSON.stringify(steps));
  console.log(JSON.stringify(await page.locator('form').evaluateAll(ns=>ns.map(n=>({action:n.action,method:n.method,fields:Array.from(n.querySelectorAll('input,textarea,select,button')).map(e=>({tag:e.tagName,name:e.name,text:e.tagName==='BUTTON'?e.textContent.trim():undefined,dataMethod:e.getAttribute('data-method')}))}))),null,2));
  await browser.close();
})().catch(e=>{console.error(e.message);process.exit(1)});
