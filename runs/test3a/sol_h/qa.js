const { chromium } = require('playwright');
(async()=>{
  const browser = await chromium.launch({headless:true});
  const page = await browser.newPage({viewport:{width:1440,height:900}, deviceScaleFactor:1});
  const logs=[]; const errors=[];
  page.on('console',m=>{ if(m.type()==='error') errors.push(m.text()); if(m.type()==='log') logs.push(m.text()); });
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:9876/index.html',{waitUntil:'networkidle',timeout:60000});
  await page.waitForFunction(()=>window.gravityLab && gravityLab.worlds.every(w=>w.object),null,{timeout:30000});
  const fps=await page.evaluate(()=>new Promise(resolve=>{let n=0,start=performance.now(),last=start,sum=0,max=0;function tick(t){if(n){const d=t-last;sum+=d;max=Math.max(max,d)}last=t;n++;if(t-start<2000)requestAnimationFrame(tick);else resolve({frames:n,fps:(n-1)*1000/sum,maxFrameMs:max});}requestAnimationFrame(tick)}));
  await page.screenshot({path:'qa-initial.png'});
  await page.click('#jumpBtn');
  await page.waitForFunction(()=>gravityLab.worlds[1].phase==='falling' && gravityLab.worlds[1].descent<0.12,null,{timeout:7000});
  await page.screenshot({path:'qa-moon-apex.png'});
  await page.waitForFunction(()=>gravityLab.worlds.every(w=>w.phase==='landed'),null,{timeout:8000});
  const result=await page.evaluate(()=>({
    earth:{apex:gravityLab.worlds[0].apex,fall:gravityLab.worlds[0].descent,state:gravityLab.worlds[0].phase},
    moon:{apex:gravityLab.worlds[1].apex,fall:gravityLab.worlds[1].descent,state:gravityLab.worlds[1].phase},
    buttonEnabled:!document.querySelector('#jumpBtn').disabled,
    labels:[document.querySelector('.earth h2').textContent,document.querySelector('.moon h2').textContent]
  }));
  console.log(JSON.stringify({title:await page.title(),canvas:await page.locator('canvas').count(),fps,result,logs,errors},null,2));
  await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
