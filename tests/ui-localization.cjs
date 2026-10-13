/* Browser regression against an isolated fixture database; no external model. */
const fs=require('fs'),assert=require('node:assert/strict');
const {chromium}=require(process.env.DECIVORA_PLAYWRIGHT_MODULE||'playwright');
(async()=>{
 const config=JSON.parse(fs.readFileSync(process.env.DECIVORA_UI_TEST_CONFIG,'utf8'));
 const browser=await chromium.launch({headless:true,...(process.env.DECIVORA_BROWSER_PATH?{executablePath:process.env.DECIVORA_BROWSER_PATH}:{})});
 try{
  const context=await browser.newContext({viewport:{width:1440,height:1100},locale:'tr-TR'}),page=await context.newPage();
  let writes=0;page.on('request',r=>{if(r.method()==='POST')writes++;});
  page.on('pageerror',e=>console.error('UI JavaScript:',e.message));page.on('response',async r=>{if(r.url().includes('/api/')&&r.status()>=400)console.error('UI API:',r.status(),(await r.json()).error);});await page.route('**/*',r=>r.request().url().startsWith(config.origin+'/')?r.continue():r.abort());
  await page.goto(config.origin+'/#'+config.bootstrap);await page.locator('#model-status').waitFor();
  assert.equal(await page.locator('html').getAttribute('lang'),'en'); // Browser language does not override English default.
  await page.locator('#conversation-text').fill('We should add a backup test. We chose SQLite. Please ask which output language to use.');
  await page.locator('#conversation-form').getByRole('button',{name:'Import conversation',exact:true}).click();
  await page.getByRole('heading',{name:'Conversation · Ready for review',exact:true}).waitFor();
  await page.getByRole('checkbox',{name:'Task · Backup test',exact:true}).check();
  const baseline=writes;
  for(const [locale,heading] of [['tr','Konuşmalar ve öneriler'],['es','Conversaciones y propuestas'],['pt-BR','Conversas e propostas'],['ar','المحادثات والمقترحات'],['en','Conversations and proposals']]){
   await page.locator('#ui-language').selectOption(locale);
   assert.equal(await page.locator('html').getAttribute('lang'),locale);
   assert.equal(await page.locator('html').getAttribute('dir'),locale==='ar'?'rtl':'ltr');
   await page.getByRole('heading',{name:heading,exact:true}).waitFor();
   assert(await page.locator('input[id^=candidate_]').first().isChecked());
   assert.equal(await page.locator('#conversation-text').inputValue(),'We should add a backup test. We chose SQLite. Please ask which output language to use.');
   assert.equal(writes,baseline,'Locale must not send a command or call a model');
  }
  await page.getByRole('button',{name:'Approve and save selected proposals',exact:true}).click();
  await page.locator('.lane[data-stage="To Do"]').getByRole('heading',{name:'Backup test',exact:true}).click();
  await page.getByText('Blocker management and history',{exact:true}).click();
  await page.locator('#blocker_reason').fill('Read access pending');await page.locator('#blocker_next_action').fill('Owner grants access');
  await page.getByRole('button',{name:'Mark as Blocked',exact:true}).click();await page.waitForFunction(()=>document.getElementById('blocker-count').textContent==='1');
  assert.equal(await page.locator('#blocker-count').textContent(),'1');assert.equal(await page.locator('.lane[data-stage="To Do"]').locator('.blocked-card').count(),1);
  await page.getByRole('button',{name:'AC / DoD',exact:true}).click();
  await page.locator('#ac').fill('User-owned acceptance draft — العربية Türkçe');
  await page.locator('#dod').fill('User-owned DoD');await page.locator('#reason').fill('User reason');
  await page.locator('[data-view=conversations]').click();await page.locator('#conversation-text').fill('Unsubmitted conversation');await page.locator('[data-view=board]').click();await page.locator('.lane[data-stage="To Do"]').getByRole('heading',{name:'Backup test',exact:true}).click();await page.getByRole('button',{name:'AC / DoD',exact:true}).click();
  await page.locator('#ui-language').selectOption('ar');
  assert.equal(await page.locator('#ac').inputValue(),'User-owned acceptance draft — العربية Türkçe');
  assert.equal(await page.locator('#dod').inputValue(),'User-owned DoD');assert.equal(await page.locator('#reason').inputValue(),'User reason');
  assert.equal(await page.locator('#conversation-text').inputValue(),'Unsubmitted conversation');
  await page.screenshot({path:process.env.DECIVORA_SCREENSHOT_DIR+'/localization-ar-desktop.png',fullPage:true});
  await page.setViewportSize({width:390,height:844});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth),false,'RTL mobile overflow');
  await page.screenshot({path:process.env.DECIVORA_SCREENSHOT_DIR+'/localization-ar-mobile.png',fullPage:true});
  await page.reload();await page.locator('.lane[data-stage="To Do"]').waitFor();assert.equal(await page.locator('html').getAttribute('lang'),'ar');
  assert.equal(await page.locator('.lane[data-stage="To Do"]').getByRole('heading',{name:'Backup test',exact:true}).count(),1);
  assert.equal(await page.locator('#blocker-count').textContent(),'1');
  await page.locator('#ui-language').selectOption('en');await page.locator('.lane[data-stage="To Do"]').getByRole('heading',{name:'Backup test',exact:true}).click();
  await page.getByText('Blocker management and history',{exact:true}).click();await page.locator('#blocker_reason').fill('Access verified');await page.locator('#blocker_next_action').fill('Resume task');await page.getByRole('button',{name:'Resolve blocker',exact:true}).click();
  await page.waitForFunction(()=>document.getElementById('blocker-count').textContent==='0');assert.equal(await page.locator('.lane[data-stage="To Do"]').locator('.card').count(),1);
  for(const locale of ['en','tr','es','pt-BR']){await page.locator('#ui-language').selectOption(locale);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth),false);}
  await page.evaluate(()=>localStorage.setItem('decivora.ui.locale.v1','unsupported'));await page.reload();await page.locator('.lane[data-stage="To Do"]').waitFor();assert.equal(await page.locator('html').getAttribute('lang'),'en');
  await page.addInitScript(()=>{Object.defineProperty(window,'localStorage',{get(){throw Error('Storage disabled');}});});
  await page.reload();await page.locator('#model-status').waitFor();await page.locator('#ui-language').selectOption('es');assert.equal(await page.locator('html').getAttribute('lang'),'es');
  console.log(JSON.stringify({locales:5,english_default:true,rtl:true,persistence:true,draft_preservation:true,selection_preservation:true,storage_fallback:true,locale_commands:0,external_model_calls:0,fixture_model:true,blocker_persisted_and_resolved:true}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
