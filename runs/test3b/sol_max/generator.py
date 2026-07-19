import json, base64, math, html
from pathlib import Path

ROOT=Path('.')
stations=json.loads((ROOT/'src_subway/dataset/capitalStations.json').read_text(encoding='utf-8-sig'))

lines=[
 {'key':'01호선','name':'1호선','year':1974,'color':'#0052A4'},
 {'key':'02호선','name':'2호선','year':1980,'color':'#00A84D'},
 {'key':'03호선','name':'3호선','year':1985,'color':'#EF7C1C'},
 {'key':'04호선','name':'4호선','year':1985,'color':'#00A4E3'},
 {'key':'수인분당선','name':'분당선 → 수인·분당선','year':1994,'color':'#FABE00'},
 {'key':'05호선','name':'5호선','year':1995,'color':'#996CAC'},
 {'key':'07호선','name':'7호선','year':1996,'color':'#747F00'},
 {'key':'08호선','name':'8호선','year':1996,'color':'#E6186C'},
 {'key':'인천선','name':'인천 1호선','year':1999,'color':'#7CA8D5'},
 {'key':'06호선','name':'6호선','year':2000,'color':'#CD7C2F'},
 {'key':'공항철도','name':'공항철도','year':2007,'color':'#0090D2'},
 {'key':'09호선','name':'9호선','year':2009,'color':'#BDB092'},
 {'key':'경의선','name':'경의선 전철 → 경의·중앙선','year':2009,'color':'#77C4A3'},
 {'key':'경춘선','name':'경춘선 전철','year':2010,'color':'#0C8E72'},
 {'key':'신분당선','name':'신분당선','year':2011,'color':'#D4003B'},
 {'key':'의정부경전철','name':'의정부 경전철','year':2012,'color':'#FDA600'},
 {'key':'용인경전철','name':'용인 에버라인','year':2013,'color':'#6FB245'},
 {'key':'인천2호선','name':'인천 2호선','year':2016,'color':'#ED8B00'},
 {'key':'경강선','name':'경강선','year':2016,'color':'#003DA5'},
 {'key':'우이신설경전철','name':'우이신설선','year':2017,'color':'#B7C452'},
 {'key':'서해선','name':'서해선','year':2018,'color':'#8FC31F'},
 {'key':'김포도시철도','name':'김포골드라인','year':2019,'color':'#A17800'},
 {'key':'SILLIM','name':'신림선','year':2022,'color':'#6789CA'},
 {'key':'GTXA','name':'GTX-A (운영 구간)','year':2024,'color':'#9A6292'},
]
selected={x['key'] for x in lines}
# compact station records
compact=[]
for s in stations:
    ls=[x for x in s['lines'] if x in selected]
    if ls:
        compact.append({'n':s['name'],'a':round(s['latitude'],6),'o':round(s['longitude'],6),'l':ls,'r':s['around_stations']})

# New lines absent from the 2021 graph source. Coordinates are OSM/Nominatim values;
# two missing Nominatim station points are interpolated between adjacent OSM points.
sillim=[
 ('샛강',37.5177651,126.9284134),('대방',37.5136467,126.9260524),
 ('서울지방병무청',37.506683,126.921232),('보라매',37.4997200,126.9197200),
 ('보라매공원',37.4958229,126.9178162),('보라매병원',37.4926570,126.9245000),
 ('당곡',37.4893988,126.9271473),('신림',37.4851675,126.9296268),
 ('서원',37.4780091,126.9323984),('서울대벤처타운',37.4722020,126.9339070),
 ('관악산(서울대)',37.469102,126.945064)
]
gtx_n=[('운정중앙',37.7159678,126.7281208),('킨텍스',37.6649857,126.7475205),('대곡',37.6317813,126.8102838),('연신내',37.6181449,126.9222105),('서울역',37.5554175,126.9725862)]
gtx_s=[('수서',37.4882235,127.1004780),('성남',37.3946138,127.1205842),('구성',37.2994354,127.1058484),('동탄',37.2003594,127.0955764)]
extra={'SILLIM':[sillim], 'GTXA':[gtx_n,gtx_s]}

data={'lines':lines,'stations':compact,'extra':extra}
font400=base64.b64encode((ROOT/'noto-400.woff2').read_bytes()).decode()
font700=base64.b64encode((ROOT/'noto-700.woff2').read_bytes()).decode()
jsdata=json.dumps(data,ensure_ascii=False,separators=(',',':'))

page=r'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=1080,initial-scale=1,maximum-scale=1,user-scalable=no"><title>서울 수도권 지하철, 1974—2026</title>
<style>
@font-face{font-family:MGNoto;src:url(data:font/woff2;base64,%%FONT400%%) format('woff2');font-weight:400;font-display:block}
@font-face{font-family:MGNoto;src:url(data:font/woff2;base64,%%FONT700%%) format('woff2');font-weight:700;font-display:block}
*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#06111c}body{display:grid;place-items:center}
#stage{display:block;width:min(100vw,56.25vh);height:min(177.7778vw,100vh);background:#06111c}
</style></head><body><canvas id="stage" width="1080" height="1920" aria-label="1974년부터 2026년까지 성장하는 서울 수도권 지하철 노선망"></canvas>
<script>
'use strict';
const DATA=%%DATA%%;
const canvas=document.getElementById('stage'),ctx=canvas.getContext('2d',{alpha:false});
const W=1080,H=1920,TOTAL=15,GROW=14,Y0=1974,Y1=2026;
const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
const ease=x=>1-Math.pow(1-clamp(x),3);
const lineByKey=Object.fromEntries(DATA.lines.map((d,i)=>[d.key,{...d,i}]));
const bounds={minLon:126.40,maxLon:127.76,minLat:36.74,maxLat:37.98};
const box={x:48,y:340,w:984,h:1190};
function project(lat,lon){return [box.x+(lon-bounds.minLon)/(bounds.maxLon-bounds.minLon)*box.w,box.y+(bounds.maxLat-lat)/(bounds.maxLat-bounds.minLat)*box.h]}
const byName={}; for(const s of DATA.stations)(byName[s.n]??=[]).push(s);
const segments={}; const points={};
for(const l of DATA.lines){segments[l.key]=[];points[l.key]=[]}
for(const s of DATA.stations){
 const p=project(s.a,s.o);
 for(const key of s.l){points[key].push({n:s.n,p,ls:s.l});
  for(const nn of s.r){const candidates=(byName[nn]||[]).filter(x=>x.l.includes(key)); if(!candidates.length)continue;
   const n=candidates.sort((a,b)=>(a.a-s.a)**2+(a.o-s.o)**2-(b.a-s.a)**2-(b.o-s.o)**2)[0];
   const id=[s.n,n.n].sort().join('|'); if(!segments[key].some(e=>e.id===id))segments[key].push({id,a:p,b:project(n.a,n.o)});
  }
 }
}
for(const [key,chains] of Object.entries(DATA.extra))for(const ch of chains){for(let i=0;i<ch.length;i++){const [n,a,o]=ch[i],p=project(a,o);points[key].push({n,p,ls:[key]});if(i)segments[key].push({id:n+i,a:project(ch[i-1][1],ch[i-1][2]),b:p})}}
for(const key in segments)segments[key].sort((a,b)=>(a.a[1]+a.a[0]*.1)-(b.a[1]+b.a[0]*.1));

const labels={
 '서울':[-24,-32,'서울역'],
 '왕십리':[24,-30,'왕십리'],
 '홍대입구':[-22,-28,'홍대입구'],
 '김포공항':[-18,-22,'김포공항'],
 '신도림':[-20,28,'신도림'],
 '강남':[22,30,'강남'],
 '잠실':[22,-26,'잠실'],
 '수서':[22,28,'수서']
};
const labelPts=[]; for(const s of DATA.stations)if(labels[s.n])labelPts.push({s,p:project(s.a,s.o),cfg:labels[s.n]});

function roundRect(x,y,w,h,r){ctx.beginPath();ctx.roundRect(x,y,w,h,r)}
function text(str,x,y,size,weight='400',align='left',color='#fff'){ctx.font=`${weight} ${size}px MGNoto, sans-serif`;ctx.textAlign=align;ctx.textBaseline='middle';ctx.fillStyle=color;ctx.fillText(str,x,y)}
function drawBackground(){
 const g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,'#071827');g.addColorStop(.52,'#07131f');g.addColorStop(1,'#040a11');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
 ctx.strokeStyle='rgba(130,190,215,.055)';ctx.lineWidth=1;for(let x=48;x<W;x+=72){ctx.beginPath();ctx.moveTo(x,300);ctx.lineTo(x,1570);ctx.stroke()}for(let y=340;y<1570;y+=72){ctx.beginPath();ctx.moveTo(34,y);ctx.lineTo(1046,y);ctx.stroke()}
 // stylized Han River context band
 ctx.beginPath();ctx.moveTo(25,920);ctx.bezierCurveTo(250,865,390,970,555,925);ctx.bezierCurveTo(745,875,860,935,1055,890);ctx.strokeStyle='rgba(66,161,194,.14)';ctx.lineWidth=34;ctx.stroke();
 ctx.beginPath();ctx.moveTo(25,920);ctx.bezierCurveTo(250,865,390,970,555,925);ctx.bezierCurveTo(745,875,860,935,1055,890);ctx.strokeStyle='rgba(104,207,232,.12)';ctx.lineWidth=2;ctx.stroke();
}
function drawHeader(year,t){
 text('SEOUL METRO • NETWORK IN MOTION',60,68,19,'700','left','#68c5df');
 text('도시를 잇는 선,',60,126,44,'700');text('52년의 성장',60,180,44,'700');
 text('1974 — 2026  ·  수도권 도시철도 주요 24개 노선',60,234,20,'400','left','#8ca5b4');
 text(String(year),1018,142,116,'700','right','#edf7fa');
 const p=clamp(t/GROW); ctx.fillStyle='rgba(119,203,222,.18)';roundRect(60,282,960,5,3);ctx.fill();ctx.fillStyle='#67c9df';roundRect(60,282,960*p,5,3);ctx.fill();
}
function lineProgress(line,t){const openT=(line.year-Y0)/(Y1-Y0)*GROW;return ease((t-openT)/.58)}
function drawGuide(){ctx.lineCap='round';ctx.lineJoin='round';for(const l of DATA.lines){ctx.strokeStyle='rgba(171,199,208,.105)';ctx.lineWidth=l.key==='GTXA'?5:3;for(const e of segments[l.key]){ctx.beginPath();ctx.moveTo(...e.a);ctx.lineTo(...e.b);ctx.stroke()}}}
function drawActive(t){
 ctx.lineCap='round';ctx.lineJoin='round';
 for(const l of DATA.lines){const lp=lineProgress(l,t);if(lp<=0)continue;const seg=segments[l.key],n=seg.length;
  ctx.shadowColor=l.color;ctx.shadowBlur=lp<1?14:5;ctx.strokeStyle=l.color;ctx.lineWidth=l.key==='GTXA'?7:5.5;
  for(let i=0;i<n;i++){const q=clamp(lp*1.18-i/Math.max(1,n)*.18);if(!q)continue;const e=seg[i],x=e.a[0]+(e.b[0]-e.a[0])*q,y=e.a[1]+(e.b[1]-e.a[1])*q;ctx.globalAlpha=.3+.7*q;ctx.beginPath();ctx.moveTo(...e.a);ctx.lineTo(x,y);ctx.stroke()}
  ctx.shadowBlur=0;ctx.globalAlpha=1;
 }
}
function stationActive(s,t){return s.l.some(k=>lineProgress(lineByKey[k],t)>.8)}
function drawStations(t){
 // ordinary station dots
 for(const l of DATA.lines){const lp=lineProgress(l,t);if(lp<.74)continue;ctx.fillStyle=l.color;ctx.globalAlpha=clamp((lp-.74)*4);for(const q of points[l.key]){ctx.beginPath();ctx.arc(q.p[0],q.p[1],2.4,0,Math.PI*2);ctx.fill()}}
 ctx.globalAlpha=1;
 // transfers: distinct white ring, only among currently active lines
 const seen=new Set();for(const s of DATA.stations){if(seen.has(s.n))continue;seen.add(s.n);const active=s.l.filter(k=>lineByKey[k]&&lineProgress(lineByKey[k],t)>.8);if(active.length<2)continue;const p=project(s.a,s.o);ctx.fillStyle='#06111c';ctx.strokeStyle='#e9f3f5';ctx.lineWidth=2.2;ctx.beginPath();ctx.arc(p[0],p[1],5.8,0,Math.PI*2);ctx.fill();ctx.stroke()}
}
function drawLabels(t){for(const q of labelPts){if(!stationActive(q.s,t))continue;const activeYears=q.s.l.filter(k=>lineByKey[k]).map(k=>lineByKey[k].year);const born=Math.min(...activeYears),openT=(born-Y0)/(Y1-Y0)*GROW;const a=clamp((t-openT-.16)/.45);if(!a)continue;const [dx,dy,name]=q.cfg;ctx.globalAlpha=a;ctx.fillStyle='rgba(5,14,23,.78)';roundRect(q.p[0]+dx-(dx<0?92:6),q.p[1]+dy-13,98,26,7);ctx.fill();text(name,q.p[0]+dx,q.p[1]+dy,13,'700',dx<0?'right':'left','#eaf4f6');ctx.globalAlpha=1}}
function drawFooter(year,t){
 const shown=DATA.lines.filter(l=>lineProgress(l,t)>=.999).length;
 const emerging=DATA.lines.filter(l=>Math.abs(l.year-year)<=1).slice(-3);
 text('NETWORK STATUS',60,1622,17,'700','left','#6dc6dc');text(`${shown} / ${DATA.lines.length}`,1020,1622,22,'700','right','#eef8fa');
 ctx.fillStyle='rgba(148,179,190,.08)';roundRect(48,1650,984,106,18);ctx.fill();
 if(emerging.length){let x=72;for(const l of emerging){ctx.fillStyle=l.color;ctx.beginPath();ctx.arc(x,1691,7,0,Math.PI*2);ctx.fill();text(l.name,x+17,1691,18,'700','left','#e9f2f4');x+=Math.min(330,65+l.name.length*19)}}else text('수도권의 생활권을 하나의 망으로',72,1691,20,'400','left','#9bb0ba');
 text(year<2026?'개통 연도 기준으로 노선이 더해집니다':'2026 · 완성된 네트워크',72,1728,17,'400','left','#78909d');
 const x0=60,x1=1020,y=1810;ctx.strokeStyle='rgba(177,204,212,.2)';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(x0,y);ctx.lineTo(x1,y);ctx.stroke();
 for(const d of [1974,1980,1990,2000,2010,2020,2026]){const x=x0+(d-Y0)/(Y1-Y0)*(x1-x0);ctx.strokeStyle=d<=year?'#6bc8de':'#38505c';ctx.beginPath();ctx.moveTo(x,y-7);ctx.lineTo(x,y+7);ctx.stroke();text(String(d),x,y+31,14,d<=year?'700':'400','center',d<=year?'#b8dce4':'#526874')}
 text('환승역',900,1875,14,'400','right','#91aab4');ctx.fillStyle='#06111c';ctx.strokeStyle='#e9f3f5';ctx.lineWidth=2;ctx.beginPath();ctx.arc(922,1875,6,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.fillStyle='#77c4d6';ctx.beginPath();ctx.arc(958,1875,3,0,Math.PI*2);ctx.fill();text('일반역',1020,1875,14,'400','right','#91aab4');
}
function render(t){t=clamp(t,0,TOTAL);const p=clamp(t/GROW),year=t>=GROW?Y1:Math.floor(Y0+(Y1-Y0)*p);drawBackground();drawHeader(year,t);drawGuide();drawActive(t);drawStations(t);drawLabels(t);drawFooter(year,t);const shown=DATA.lines.filter(l=>lineProgress(l,t)>=.999).length;window.__mg={t:+t.toFixed(3),year,lines_shown:shown};}
window.__renderAt=ms=>render(ms/1000);
let start=null;function frame(now){if(start===null)start=now;const t=Math.min(TOTAL,(now-start)/1000);render(t);if(t<TOTAL)requestAnimationFrame(frame)}
document.fonts.ready.then(()=>{window.__mgReady=true;requestAnimationFrame(frame)});
</script></body></html>'''
page=page.replace('%%FONT400%%',font400).replace('%%FONT700%%',font700).replace('%%DATA%%',jsdata)
(ROOT/'index.html').write_text(page,encoding='utf-8')
print(f"index.html written: {len(page):,} chars; {len(lines)} lines; {len(compact)} stations")
