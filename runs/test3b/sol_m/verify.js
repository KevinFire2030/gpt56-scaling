const puppeteer = require('puppeteer-core');
const path = require('path');
(async()=>{
  const chrome='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
  const browser=await puppeteer.launch({executablePath:chrome,headless:true,args:['--no-sandbox','--disable-gpu','--allow-file-access-from-files']});
  const page=await browser.newPage();
  await page.setViewport({width:1080,height:1920,deviceScaleFactor:1});
  const consoleErrors=[],pageErrors=[],externalRequests=[],failedRequests=[];
  page.on('console',m=>{ if(m.type()==='error') consoleErrors.push(m.text()); });
  page.on('pageerror',e=>pageErrors.push(String(e)));
  page.on('request',r=>{if(/^https?:/i.test(r.url())) externalRequests.push(r.url())});
  page.on('requestfailed',r=>failedRequests.push({url:r.url(),error:r.failure()?.errorText}));
  const url='file:///'+path.resolve('index.html').replace(/\\/g,'/');
  await page.goto(url,{waitUntil:'load'});
  const samples=[];
  for(const target of [0,1,3,5,7,9,11,13,14,15]){
    if(target>0) await page.waitForFunction(x=>window.__mg && window.__mg.t>=x,{timeout:17000},target);
    samples.push(await page.evaluate(()=>({...window.__mg})));
  }
  const at15=await page.evaluate(()=>({mg:{...window.__mg},offsets:[...document.querySelectorAll('.active-geom')].map(x=>+x.style.strokeDashoffset),yearText:document.querySelector('#year').firstChild.nodeValue.trim(),countText:document.querySelector('#lineCount').textContent}));
  await new Promise(r=>setTimeout(r,600));
  const afterHold=await page.evaluate(()=>({...window.__mg}));
  await page.screenshot({path:'final.png',fullPage:false});
  const result={url,viewport:{width:1080,height:1920},samples,at15,afterHold,consoleErrors,pageErrors,externalRequests,failedRequests};
  require('fs').writeFileSync('verification-results.json',JSON.stringify(result,null,2));
  console.log(JSON.stringify(result,null,2));
  await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
