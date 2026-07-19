import base64, html, json, re, xml.etree.ElementTree as ET

LINES = [
  dict(id='l1',name='1호선',year=1974,color='#0052A4',path='cls-65',station='cls-36'),
  dict(id='l2',name='2호선',year=1980,color='#00A84D',path='cls-22',station='cls-45'),
  dict(id='l3',name='3호선',year=1985,color='#EF7C1C',path='cls-13',station='cls-19'),
  dict(id='l4',name='4호선',year=1985,color='#00A5DE',path='cls-15',station='cls-8'),
  dict(id='suin',name='수인·분당선',year=1994,color='#F5A200',path='cls-57',station='cls-42'),
  dict(id='l5',name='5호선',year=1995,color='#996CAC',path='cls-55',station='cls-50'),
  dict(id='l7',name='7호선',year=1996,color='#747F00',path='cls-20',station='cls-49'),
  dict(id='l8',name='8호선',year=1996,color='#E6186C',path='cls-23',station='cls-9'),
  dict(id='incheon1',name='인천 1호선',year=1999,color='#7CA8D5',path='cls-18',station='cls-21'),
  dict(id='l6',name='6호선',year=2000,color='#CD7C2F',path='cls-58',station='cls-37'),
  dict(id='gj',name='경의·중앙선',year=2005,color='#77C4A3',path='cls-44',station='cls-61'),
  dict(id='arex',name='공항철도',year=2007,color='#0090D2',path='cls-30',station='cls-5'),
  dict(id='l9',name='9호선',year=2009,color='#BDB092',path='cls-43',station='cls-17'),
  dict(id='gc',name='경춘선',year=2010,color='#0C8E72',path='cls-14',station='cls-16'),
  dict(id='shinbundang',name='신분당선',year=2011,color='#D4003B',path='cls-64',station='cls-40'),
  dict(id='uline',name='의정부경전철',year=2012,color='#FDA600',path='cls-26',station='cls-12'),
  dict(id='ever',name='에버라인',year=2013,color='#6FB245',path='cls-29',station='cls-52'),
  dict(id='gg',name='경강선',year=2016,color='#0054A6',path='cls-59',station='cls-27'),
  dict(id='incheon2',name='인천 2호선',year=2016,color='#ED8B00',path='cls-33',station='cls-63'),
  dict(id='ui',name='우이신설선',year=2017,color='#B7C452',path='cls-32',station='cls-62'),
  dict(id='seohae',name='서해선',year=2018,color='#8FC31F',path='cls-24',station='cls-56'),
  dict(id='gimpo',name='김포골드라인',year=2019,color='#A17800',path='cls-11',station='cls-6'),
  dict(id='sillim',name='신림선',year=2022,color='#6789CA',path='cls-46',station='cls-34'),
  dict(id='gtxa',name='GTX-A',year=2024,color='#9A6292',path=None,station=None),
]

root = ET.parse('source_map.svg').getroot()
def tag_name(e): return e.tag.rsplit('}',1)[-1]
def make_tag(e, cls, extra=''):
    attrs=[]
    for k,v in e.attrib.items():
        if k == 'class': continue
        attrs.append(f'{k}="{html.escape(v, quote=True)}"')
    return f'<{tag_name(e)} class="{cls}" {" ".join(attrs)} {extra}/>'

def selected_by_class(class_name, allowed=('path','line','polyline')):
    return [e for e in root.iter() if e.attrib.get('class')==class_name and tag_name(e) in allowed]

def in_main_circle(e):
    try:
        x=float(e.attrib.get('cx','-1')); y=float(e.attrib.get('cy','-1'))
        return 1200 <= x <= 7100 and 450 <= y <= 5950
    except: return False

all_groups=[]; all_guides=[]
for line in LINES:
    if line['id']=='gtxa':
        gray=selected_by_class('cls-53')
        geoms=[gray[13],gray[17]]  # source-map planned geometry: Suseo–Dongtan and Unjeong–Seoul portions
    else:
        geoms=selected_by_class(line['path'])
    guide=''.join(make_tag(e,'guide-geom') for e in geoms)
    active=''.join(make_tag(e,'active-geom') for e in geoms)
    stations=[] if not line['station'] else [e for e in selected_by_class(line['station'],('circle','ellipse')) if in_main_circle(e)]
    dots=''.join(make_tag(e,'station-dot') for e in stations)
    all_guides.append(f'<g data-guide="{line["id"]}">{guide}</g>')
    all_groups.append(f'<g class="route" data-id="{line["id"]}" data-year="{line["year"]}" data-name="{line["name"]}" data-color="{line["color"]}" style="--c:{line["color"]}">{active}{dots}</g>')

major = [
 ('서울역',4200,2430,1974),('시청',4308,2285,1974),('종로3가',4520,2128,1974),
 ('강남',4935,3175,1982),('고속터미널',4735,2996,1985),('왕십리',5168,2358,1983),
 ('여의도',3854,2808,1996),('김포공항',2640,2175,1996),('건대입구',5425,2518,1980)
]
major_svg=''.join(f'''<g class="major" data-year="{yr}" transform="translate({x} {y})"><circle class="transfer-halo" r="21"/><circle class="transfer-core" r="8"/><text x="28" y="9">{n}</text></g>''' for n,x,y,yr in major)

font_reg=base64.b64encode(open('Pretendard-Regular.woff2','rb').read()).decode()
font_bold=base64.b64encode(open('Pretendard-Bold.woff2','rb').read()).decode()
lines_json=json.dumps([{k:v for k,v in x.items() if k in ('id','name','year','color')} for x in LINES],ensure_ascii=False)

page=f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1"><title>서울 수도권 전철 1974—2026</title>
<style>
@font-face{{font-family:Pretendard;src:url(data:font/woff2;base64,{font_reg}) format('woff2');font-weight:400;font-display:block}}
@font-face{{font-family:Pretendard;src:url(data:font/woff2;base64,{font_bold}) format('woff2');font-weight:700;font-display:block}}
*{{box-sizing:border-box}}html,body{{margin:0;width:100%;height:100%;overflow:hidden;background:#030912}}body{{display:grid;place-items:center;font-family:Pretendard,sans-serif;color:#f4f8ff}}
#stage{{position:relative;width:1080px;height:1920px;overflow:hidden;flex:none;background:radial-gradient(ellipse at 52% 43%,#132238 0,#07111e 43%,#02070d 100%);transform-origin:center}}
#stage:before{{content:"";position:absolute;inset:0;pointer-events:none;background-image:linear-gradient(rgba(255,255,255,.018) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.018) 1px,transparent 1px);background-size:54px 54px;mask-image:linear-gradient(to bottom,transparent,#000 18%,#000 80%,transparent)}}
header{{position:absolute;z-index:5;left:72px;right:72px;top:72px}}
.kicker{{display:flex;align-items:center;gap:14px;font-size:22px;letter-spacing:.22em;color:#77a2c9;font-weight:700}}.kicker:before{{content:"";width:36px;height:3px;background:#71d6ff;border-radius:9px;box-shadow:0 0 14px #71d6ff}}
h1{{margin:22px 0 0;font-size:54px;line-height:1.12;letter-spacing:-.04em}}h1 span{{color:#91a9c2;font-weight:400}}
#yearBox{{position:absolute;z-index:6;top:255px;left:72px;right:72px;display:flex;align-items:end;justify-content:space-between;border-bottom:1px solid rgba(174,212,240,.18);padding-bottom:24px}}
#year{{font-size:130px;line-height:.78;letter-spacing:-.065em;font-weight:700;font-variant-numeric:tabular-nums}}#year small{{font-size:30px;letter-spacing:0;color:#6f8fab;margin-left:14px}}
#status{{text-align:right}}#lineName{{font-size:28px;font-weight:700;min-height:40px}}#lineCount{{font-size:19px;color:#6f8fab;margin-top:8px;font-variant-numeric:tabular-nums}}
#mapWrap{{position:absolute;left:36px;right:36px;top:390px;height:1200px;filter:drop-shadow(0 16px 50px rgba(0,0,0,.45))}}
#map{{width:100%;height:100%;overflow:visible}}
.guide-geom{{fill:none;stroke:#a8c0d4;stroke-width:16;stroke-linecap:round;stroke-linejoin:round;opacity:.095;vector-effect:non-scaling-stroke}}
.active-geom{{fill:none;stroke:var(--c);stroke-width:18;stroke-linecap:round;stroke-linejoin:round;opacity:0;vector-effect:non-scaling-stroke;filter:drop-shadow(0 0 7px color-mix(in srgb,var(--c) 55%,transparent))}}
.station-dot{{fill:#07111e;stroke:var(--c);stroke-width:10;opacity:0;vector-effect:non-scaling-stroke}}
.major{{opacity:0;filter:drop-shadow(0 0 16px rgba(255,255,255,.26))}}.transfer-halo{{fill:#07111e;stroke:#fff;stroke-width:10;vector-effect:non-scaling-stroke}}.transfer-core{{fill:#fff}}.major text{{fill:#fff;font-size:74px;font-weight:700;paint-order:stroke;stroke:#07111e;stroke-width:18;stroke-linejoin:round}}
#legend{{position:absolute;z-index:6;left:72px;right:72px;bottom:150px;display:grid;grid-template-columns:repeat(4,1fr);gap:16px 20px}}
.chip{{display:flex;align-items:center;gap:11px;color:#6f8298;font-size:17px;white-space:nowrap;transition:none}}.chip i{{width:18px;height:5px;border-radius:8px;background:var(--c);box-shadow:0 0 8px color-mix(in srgb,var(--c) 45%,transparent)}}.chip.on{{color:#e7f2ff}}.chip strong{{font-weight:700}}
footer{{position:absolute;left:72px;right:72px;bottom:66px;display:flex;justify-content:space-between;align-items:center;color:#4f6a82;font-size:15px;letter-spacing:.03em}}#progress{{position:absolute;bottom:0;left:0;height:5px;width:0;background:linear-gradient(90deg,#4ac9ff,#fff);box-shadow:0 0 16px #4ac9ff}}
</style></head><body><main id="stage">
<header><div class="kicker">SEOUL METROPOLITAN RAIL</div><h1>서울의 선들이<br><span>도시를 연결한 52년</span></h1></header>
<section id="yearBox"><div id="year">1974<small>년</small></div><div id="status"><div id="lineName">1호선</div><div id="lineCount">0 / {len(LINES)} LINES</div></div></section>
<div id="mapWrap"><svg id="map" viewBox="1200 430 5900 5550" preserveAspectRatio="none" aria-label="서울 수도권 전철 노선 성장 지도"><g id="guides">{''.join(all_guides)}</g><g id="routes">{''.join(all_groups)}</g><g id="majorStations">{major_svg}</g></svg></div>
<div id="legend"></div><footer><span>SCHEMATIC NETWORK · NO AUDIO</span><span>CC BY-SA 4.0 · Wikimedia Commons adaptation</span></footer><div id="progress"></div></main>
<script>
(()=>{{'use strict';
const stage=document.getElementById('stage');function fit(){{stage.style.transform=`scale(${{Math.min(innerWidth/1080,innerHeight/1920)}})`}}fit();addEventListener('resize',fit);
const DATA={lines_json};
const duration=15, growthEnd=14, startYear=1974, endYear=2026;
const yearEl=document.getElementById('year'),lineName=document.getElementById('lineName'),lineCount=document.getElementById('lineCount'),progress=document.getElementById('progress'),legend=document.getElementById('legend');
legend.innerHTML=DATA.map(d=>`<div class="chip" data-id="${{d.id}}" style="--c:${{d.color}}"><i></i><span><strong>${{d.name}}</strong> · ${{d.year}}</span></div>`).join('');
const routes=[...document.querySelectorAll('.route')].map(g=>{{
 const paths=[...g.querySelectorAll('.active-geom')]; const lengths=paths.map(p=>{{const v=p.getTotalLength();p.style.strokeDasharray=`${{v}} ${{v}}`;p.style.strokeDashoffset=v;return v}});
 return {{g,paths,lengths,year:+g.dataset.year,name:g.dataset.name,id:g.dataset.id,dots:[...g.querySelectorAll('.station-dot')]}};
}});
const majors=[...document.querySelectorAll('.major')];
function clamp(x,a=0,b=1){{return Math.max(a,Math.min(b,x))}} function ease(x){{x=clamp(x);return 1-Math.pow(1-x,3)}}
let zero=null,raf=0,lastYear=-1;
function render(t){{
 t=clamp(t,0,duration); const yf=startYear+(endYear-startYear)*clamp(t/growthEnd); const yi=Math.min(endYear,Math.floor(yf+1e-7));
 let shown=0,current='';
 routes.forEach(r=>{{const raw=clamp((yf-r.year)/1.8);const q=ease(raw);if(raw>0)current=r.name;if(raw>=1)shown++;r.paths.forEach((p,i)=>{{p.style.opacity=raw>0?1:0;p.style.strokeDashoffset=r.lengths[i]*(1-q)}});r.dots.forEach(d=>d.style.opacity=raw>.45?(.18+.82*q):0);document.querySelector(`.chip[data-id="${{r.id}}"]`).classList.toggle('on',raw>=1)}});
 majors.forEach(m=>{{const q=clamp((yf-(+m.dataset.year))/1.2);m.style.opacity=q}});
 if(yi!==lastYear){{yearEl.firstChild.nodeValue=String(yi);lastYear=yi}} lineName.textContent=t>=growthEnd?'2026 · 현재의 네트워크':(current||'도시의 첫 번째 선');lineCount.textContent=`${{shown}} / ${{DATA.length}} LINES`;progress.style.width=`${{t/duration*100}}%`;
 window.__mg={{t:+t.toFixed(3),year:yi,lines_shown:shown}};
}}
function tick(now){{if(zero===null)zero=now;const t=Math.min((now-zero)/1000,duration);render(t);if(t<duration)raf=requestAnimationFrame(tick)}}
window.__mg={{t:0,year:1974,lines_shown:0}};window.__mgRender=render;requestAnimationFrame(tick);
}})();
</script></body></html>'''
open('index.html','w',encoding='utf-8').write(page)
print(f'index.html: {len(page):,} chars; lines={len(LINES)}')
