from pathlib import Path
from playwright.sync_api import sync_playwright
import json, time, hashlib, base64

root=Path('.').resolve()
url=(root/'index.html').as_uri()
console_errors=[]; page_errors=[]; requests=[]; failed=[]; samples=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    page=browser.new_page(viewport={'width':1080,'height':1920}, device_scale_factor=1)
    page.on('console',lambda m: console_errors.append({'type':m.type,'text':m.text}) if m.type=='error' else None)
    page.on('pageerror',lambda e: page_errors.append(str(e)))
    page.on('request',lambda r: requests.append(r.url))
    page.on('requestfailed',lambda r: failed.append({'url':r.url,'failure':r.failure}))
    page.goto(url,wait_until='load')
    page.wait_for_function('window.__mgReady === true && window.__mg && window.__mg.t >= 0')
    targets=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
    for target in targets:
        if target:
            page.wait_for_function('(v)=>window.__mg.t>=v',arg=target,timeout=3000)
        mg=page.evaluate('window.__mg')
        samples.append(mg)
    page.screenshot(path=str(root/'final.png'))
    png1=page.locator('#stage').screenshot()
    mg15=page.evaluate('window.__mg')
    page.wait_for_timeout(700)
    png2=page.locator('#stage').screenshot()
    mg_after=page.evaluate('window.__mg')
    dims=page.evaluate('({canvas:[stage.width,stage.height],scroll:[document.documentElement.scrollWidth,document.documentElement.scrollHeight],viewport:[innerWidth,innerHeight],overflow:getComputedStyle(document.body).overflow})')
    browser.close()
external=[u for u in requests if u.startswith(('http://','https://'))]
result={
 'url':url,'console_errors':console_errors,'page_errors':page_errors,'failed_requests':failed,
 'external_runtime_requests':external,'all_request_count':len(requests),'samples':samples,
 'at_15':mg15,'after_15_7':mg_after,'final_frame_identical_after_hold':png1==png2,
 'final_frame_sha256':hashlib.sha256(png1).hexdigest(),'dimensions':dims,
 'final_png_bytes':len(png1)
}
Path('verification_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
