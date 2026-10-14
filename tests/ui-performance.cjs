/* Read-only application timing: isolated browser context, no user record writes. */
const fs=require('fs'),{chromium}=require(process.env.DECIVORA_PLAYWRIGHT_MODULE||'playwright');
const now=()=>performance.now();
function stats(v){v.sort((a,b)=>a-b);return {samples:v.length,median_ms:+v[Math.floor(v.length/2)].toFixed(2),p95_ms:+v[Math.ceil(v.length*.95)-1].toFixed(2),max_ms:+v.at(-1).toFixed(2)};}
(async()=>{
 const meta=JSON.parse(fs.readFileSync(process.env.DECIVORA_PERF_SESSION_FILE,'utf8'));
 if(meta.origin!=='http://127.0.0.1:53610')throw Error('Unexpected origin');
 const browser=await chromium.launch({headless:true,executablePath:process.env.DECIVORA_BROWSER_PATH});
 const result={date:'2026-10-14',synthetic_browser_context:true,actual_local_services:true,model_calls:0,user_record_writes:0,surfaces:[]};
 try{
  for(const surface of ['tracker','product']){
   const context=await browser.newContext({viewport:{width:1440,height:1000}});const page=await context.newPage();let errors=0;page.on('pageerror',()=>errors++);
   await page.route('**/*',r=>r.request().url().startsWith('http://127.0.0.1:')?r.continue():r.abort());
   const ready=[],dcl=[];
   for(let i=0;i<11;i++){
    const start=now();if(i===0)await page.goto(surface==='tracker'?'http://127.0.0.1:8765/':meta.origin+'/#'+meta.bootstrap,{waitUntil:'domcontentloaded'});else await page.reload({waitUntil:'domcontentloaded'});const dom=now();
    if(surface==='tracker')await page.waitForFunction(()=>document.getElementById('delivered-count').textContent==='56');
    else await page.waitForFunction(()=>document.getElementById('project-selector').options.length>0&&document.getElementById('model-status').textContent.length>0);
    ready.push(now()-start);dcl.push(dom-start);
   }
   let interaction;
   if(surface==='product'){
    const values=[];
    for(let i=0;i<10;i++){await page.locator('[data-view="conversations"]').click();const start=now();await page.locator('[data-view="board"]').click();await page.locator('#board').waitFor({state:'visible'});values.push(now()-start);}
    interaction=stats(values);
   }
   result.surfaces.push({surface,first_load_ready_ms:+ready[0].toFixed(2),subsequent_ready:stats(ready.slice(1)),subsequent_domcontentloaded:stats(dcl.slice(1)),board_navigation:interaction||null,page_errors:errors});await context.close();
  }
 }finally{await browser.close();}
 fs.writeFileSync(process.env.DECIVORA_PERF_BROWSER_OUTPUT,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
})().catch(e=>{console.error(e.message);process.exitCode=1});
