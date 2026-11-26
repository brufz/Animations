"""Monta ep3.html (césio-137) a partir de ep3/manifest.json, ep3/act/act.json e timing.json"""
import json, os, re
D = '/home/claude/cesio'; A = f'{D}/ep3'
src = open('/home/claude/holanda/build_ep2.py').read()
grab = lambda name: re.search(name + r' = r"""(.*?)"""', src, re.S).group(1)
CSS, JS0, TAIL0 = grab('CSS'), grab('JS'), grab('TAIL')
MAN = json.load(open(f'{A}/manifest.json')); ACT = json.load(open(f'{A}/act/act.json')) if os.path.exists(f'{A}/act/act.json') else {}
TM = json.load(open(f'{D}/timing.json')); DUR = round(TM['dur'], 2)
JS = JS0.replace("const A='file:///home/claude/holanda/ep2/'", "const A='file:///home/claude/cesio/ep3/'").replace('const PB=__PB__;', '')
CSS += r"""
.glow{position:absolute;transform:translate(-50%,-50%);border-radius:50%;mix-blend-mode:screen;pointer-events:none}
.sign{display:flex;align-items:center;justify-content:center;font-family:RB;font-weight:900;font-stretch:78%;letter-spacing:3px;white-space:nowrap}
.stone{position:absolute;width:34px;height:27px;border-radius:45%;background:radial-gradient(circle at 35% 35%,#8a847c,#4a4640);box-shadow:0 3px 4px rgba(0,0,0,.35)}
#gauge{position:absolute;left:290px;top:250px;width:500px;height:330px;opacity:0}
.chip{display:inline-block;width:64px;height:64px;border-radius:14px;vertical-align:middle;margin-right:18px;box-shadow:inset 0 0 0 4px rgba(255,255,255,.6)}
"""
SCENES_JS = r"""
const M3=MAN;
function plate(S,src,par,extra){return img(S,src,-M,0,par,extra||{})}
function actorsOf(tag,filter){const D=ACT[tag];if(!D)return [];return D.actors.filter(a=>!filter||filter(a))}
function addActors(S,tag,filter){const D=ACT[tag];if(!D)return;S.actD=S.actD||[];actorsOf(tag,filter).forEach(a=>{const it=img(S,a.frames[0],a.x-M,a.y,a.par);it.fr=a.frames;it.k=0;it.t0=D.t0;it.vis=a.vis;it.who=a.who;S.actD.push(it)})}
function actorsUpd(S,T){(S.actD||[]).forEach(it=>{const i=clamp(Math.round((T-it.t0)*30),0,it.fr.length-1);if(i!==it.k){it.k=i;it.e.src=A+it.fr[i]}
  if(it.vis){const t=T-it.t0;it.e.style.opacity=Math.min(prog(t,it.vis[0],it.vis[0]+.3),1-prog(t,it.vis[1]-.2,it.vis[1]))}})}
function glow(S,x,y,r,par,col){const e=document.createElement('div');e.className='glow';e.style.width=e.style.height=(2*r)+'px';e.style.background=`radial-gradient(circle,${col||'rgba(120,210,255,.95)'} 0%,rgba(70,160,255,.45) 30%,rgba(40,120,255,0) 70%)`;S.el.appendChild(e);const it={e,x:x-M,y,par,isGlow:1};S.items.push(it);return it}
function pan(S,cx){S.items.forEach(it=>{it.e.style.left=(it.x+cx*it.par)+'px';it.e.style.top=it.y+'px';it.e.style.transform=(it.isDiv?'translate(-50%,-100%) ':it.isGlow?'translate(-50%,-50%) ':'')+(it.extra||'')})}
function tagAt(S,txt,x,y,par){return div(S,'tag',txt,x-M,y,par??.6)}
function quadText(S,html,w,h,q,par){const it=div(S,'abs',`<div class="sign" style="width:${w}px;height:${h}px">${html}</div>`,-M,0,par);it.e.style.transformOrigin='0 0';it.isDiv=0;it.m=homog(w,h,q.map(p=>[p[0],p[1]]));it.extra=it.m;return it}
function popTag(it,T,a,b){pop(it,T,a,b)}
const SC=(t0,t1,b,u)=>scene(t0,t1,b,u);
const L=n=>M3[n].layers,PT=n=>M3[n].pts;
// 0 GANCHO — 19 gramas de pó azul
SC(0,2.45,S=>{plate(S,L('hook').bg,.5);plate(S,L('hook').glow,.5);const p=PT('hook').po;S.g=glow(S,p[0],p[1],330,.5);S.g2=glow(S,p[0]-260,p[1]-90,170,.5)},
 (S,t,T)=>{pan(S,kf(t,[[0,30],[2.45,-30]]));const f=.75+.25*Math.sin(T*6)+.08*Math.sin(T*17);S.g.e.style.opacity=f;S.g2.e.style.opacity=f*.7;S.g.extra=` scale(${1+.04*Math.sin(T*5)})`});
// 1 6 MIL TONELADAS
SC(2.45,6.4,S=>{plate(S,L('tonel').bg,.6)},(S,t,T)=>{pan(S,kf(t,[[0,-40],[3.95,40]]))});
// 2 MAPA — Goiânia, 1987
SC(6.4,9.4,S=>{const m=M3.mapa;S.map=img(S,m.src,-M,0,.3);
  const sv=document.createElementNS('http://www.w3.org/2000/svg','svg');sv.setAttribute('width',1300);sv.setAttribute('height',1920);sv.style.position='absolute';sv.style.left=-M+'px';sv.style.top='0';
  const d='M'+m.br.map(p=>p[0].toFixed(1)+','+p[1].toFixed(1)).join(' L')+'Z';sv.innerHTML=`<path d="${d}" fill="rgba(255,230,120,.12)" stroke="#fff6dc" stroke-width="7" stroke-dasharray="22 16" stroke-linejoin="round"/>`;
  S.el.appendChild(sv);S.items.push({e:sv,x:-M,y:0,par:.3});S.sv=sv;S.t=tagAt(S,'GOIÂNIA<small>1987</small>',m.pin[0],m.pin[1]-30,.3)},
 (S,t,T)=>{pan(S,kf(t,[[0,-30],[3,30]]));S.sv.style.opacity=prog(t,.1,.6);const L2=S.sv.querySelector('path');L2.style.strokeDashoffset=(-t*40)+'';popTag(S.t,T,7.2)});
// 3 A CLÍNICA ABANDONADA
SC(9.4,12.6,S=>{plate(S,L('clin').bg,.5);plate(S,L('clin').fg,1.6);const p=PT('clin').maq;S.t=tagAt(S,'RADIOTERAPIA',p[0],p[1]-40,.5)},(S,t,T)=>{pan(S,kf(t,[[0,40],[3.2,-40]]));popTag(S.t,T,11.4)});
// 4 CATADORES LEVAM A PEÇA
SC(12.6,15.7,S=>{plate(S,L('clin2').bg,.6);addActors(S,'clin2')},(S,t,T)=>{actorsUpd(S,T);pan(S,kf(t,[[0,-25],[3.1,25]]))});
// 5 FERRO-VELHO
SC(15.7,17.3,S=>{plate(S,L('ferro').bg,.6);S.s=quadText(S,'<span style="font-size:150px;color:#c0392b">FERRO VELHO</span>',1100,230,PT('ferro').placa,.6);addActors(S,'ferro')},(S,t,T)=>{actorsUpd(S,T);pan(S,kf(t,[[0,30],[1.6,-10]]))});
// 6 À NOITE, O BRILHO AZUL
SC(17.3,20.8,S=>{plate(S,L('noite').bg,.6);const l=PT('noite').lamp;S.l=glow(S,l[0],l[1],300,.6,'rgba(255,210,140,.8)');addActors(S,'noite');plate(S,L('noite').mesa,.7);plate(S,L('noite').glow,.7);const p=PT('noite').peca;S.g=glow(S,p[0],p[1],420,.7)},
 (S,t,T)=>{actorsUpd(S,T);pan(S,kf(t,[[0,-20],[3.5,20]]));const k=prog(t,.3,1.6);S.g.e.style.opacity=(.55+.25*Math.sin(T*5))*k+.05;S.l.e.style.opacity=.5});
// 7 REPARTE COM A FAMÍLIA
SC(20.8,22.4,S=>{plate(S,L('noite2').bg,.6);const l=PT('noite2').lamp;S.l=glow(S,l[0],l[1],260,.6,'rgba(255,210,140,.75)');addActors(S,'noite2',a=>a.who!=='menino');plate(S,L('noite2').mesa,.7);plate(S,L('noite2').glow,.7);addActors(S,'noite2',a=>a.who==='menino');const p=PT('noite2').peca;S.g=glow(S,p[0],p[1],360,.7)},
 (S,t,T)=>{actorsUpd(S,T);pan(S,kf(t,[[0,25],[1.6,-5]]));S.g.e.style.opacity=.6+.25*Math.sin(T*5);S.l.e.style.opacity=.45});
// 8 LEIDE BRINCA COM O PÓ
SC(22.4,25.8,S=>{plate(S,L('coz1').room,.5);const l=PT('coz1').lamp;S.l=glow(S,l[0],l[1],260,.5,'rgba(255,220,160,.7)');plate(S,L('coz1').mesa,.8);plate(S,L('coz1').glow,.8);addActors(S,'coz1');const p=PT('coz1').po;S.g=glow(S,p[0],p[1],260,.8);S.t=tagAt(S,'LEIDE<small>6 ANOS</small>',p[0]-40,p[1]-560,.7)},
 (S,t,T)=>{actorsUpd(S,T);pan(S,kf(t,[[0,-20],[3.4,20]]));S.g.e.style.opacity=.45+.2*Math.sin(T*7);S.l.e.style.opacity=.35;popTag(S.t,T,23.2)});
// 9 NO JANTAR
SC(25.8,28.1,S=>{plate(S,L('coz2').room,.5);const l=PT('coz2').lamp;S.l=glow(S,l[0],l[1],240,.5,'rgba(255,220,160,.7)');addActors(S,'coz2',a=>a.who!=='leide');plate(S,L('coz2').mesa,.8);plate(S,L('coz2').glow,.8);addActors(S,'coz2',a=>a.who==='leide');const p=PT('coz2').po;S.g=glow(S,p[0],p[1],200,.8)},
 (S,t,T)=>{actorsUpd(S,T);pan(S,kf(t,[[0,20],[2.3,-20]]));S.g.e.style.opacity=(.35+.15*Math.sin(T*7))*(1-prog(t,1.,2.));S.l.e.style.opacity=.35});
// 10 DE ÔNIBUS
SC(28.1,30.4,S=>{plate(S,L('onibus').bg,.4);S.bus=[];addActors(S,'onibus');S.bus.push(...(S.actD||[]));S.bus.push(plate(S,L('onibus').bus,1));S.t=tagAt(S,'MARIA GABRIELA',650,560,0)},
 (S,t,T)=>{actorsUpd(S,T);pan(S,kf(t,[[0,15],[2.3,-15]]));const bx=kf(t,[[0,-1100],[2.3,520]]);S.bus.forEach(it=>{it.e.style.left=(it.x+bx)+'px'});popTag(S.t,T,28.6);S.t.e.style.transform='translate(-50%,-100%)'+S.t.extra});
// 11 À VIGILÂNCIA SANITÁRIA
SC(30.4,32.6,S=>{plate(S,L('vig').bg,.6);S.s=quadText(S,'<span style="font-size:118px;color:#1d5fa8">VIGILÂNCIA SANITÁRIA</span>',1500,260,PT('vig').placa,.6);addActors(S,'vig')},(S,t,T)=>{actorsUpd(S,T);pan(S,kf(t,[[0,-30],[2.2,10]]))});
// 12 O FÍSICO MEDE (dois detectores)
SC(32.6,39.1,S=>{plate(S,L('escr').room,.5);addActors(S,'escr');plate(S,L('escr').mesa,.8);const b=PT('escr').bolsa;S.g=glow(S,b[0],b[1],180,.8)},
 (S,t,T)=>{actorsUpd(S,T);pan(S,kf(t,[[0,25],[6.5,-25]]));S.g.e.style.opacity=.25+.1*Math.sin(T*6)});
// 13 O BOMBEIRO E O GRITO
SC(39.1,44.6,S=>{plate(S,L('vig').bg,.6);S.s=quadText(S,'<span style="font-size:118px;color:#1d5fa8">VIGILÂNCIA SANITÁRIA</span>',1500,260,PT('vig').placa,.6);addActors(S,'vig2');
  const f=actorsOf('vig2',a=>a.who==='fisico')[0];S.b=div(S,'bub','Pelo amor de Deus, não!',(f?f.x-M+f.w*.55:540),(f?f.y+f.h*.08:700),.8);S.b.e.style.setProperty('--tx','30%')},
 (S,t,T)=>{actorsUpd(S,T);pan(S,kf(t,[[0,-35],[5.5,35]]));pop(S.b,T,42.95)});
// 14 ESTÁDIO — 112 MIL EXAMINADOS
SC(44.6,48.1,S=>{plate(S,L('estadio').bg,.5);addActors(S,'estadio');plate(S,L('estadio').fg,1.6,{opacity:.6})},(S,t,T)=>{actorsUpd(S,T);pan(S,kf(t,[[0,-40],[3.5,40]]))});
// 15 MEMORIAL — Leide e Maria Gabriela
SC(48.1,51.1,S=>{plate(S,L('memo').bg,.5);plate(S,L('memo').chama,.5);const q=PT('memo');S.v1=glow(S,q.v1[0],q.v1[1],120,.5,'rgba(255,200,120,.9)');S.v2=glow(S,q.v2[0],q.v2[1],120,.5,'rgba(255,200,120,.9)');
  S.s=quadText(S,'<div style="text-align:center;font-family:SERIF;color:#4a4540;line-height:1.25"><div style="font-size:84px">Leide</div><div style="font-size:84px">Maria Gabriela</div><div style="font-size:60px;margin-top:14px">23 · 10 · 1987</div></div>',1000,560,q.lapide,.5);S.el.style.filter='saturate(.75)'},
 (S,t,T)=>{pan(S,kf(t,[[0,20],[3,-20]]));const f=.8+.15*Math.sin(T*13)+.05*Math.sin(T*29);S.v1.e.style.opacity=f;S.v2.e.style.opacity=f*.95;S.s.e.style.opacity=prog(t,.2,.9)});
// 16 O ENTERRO
SC(51.1,53.7,S=>{plate(S,L('enterro').bg,.6);addActors(S,'enterro');plate(S,L('enterro').fg,1.6,{opacity:.6});S.el.style.filter='saturate(.8)';
  const c=PT('enterro');S.st=[];for(let i=0;i<9;i++){const e=document.createElement('div');e.className='stone';S.el.appendChild(e);const tx=(i%2?c.c1:c.c2);S.st.push({e,t0:.35+i*.22,x1:tx[0]-M+(Math.sin(i*7.3)*170),y1:tx[1]+40+Math.cos(i*3.1)*40,x0:1150+(i%3)*30,y0:300+(i*53)%220})}},
 (S,t,T)=>{actorsUpd(S,T);const cx=kf(t,[[0,-20],[2.6,20]]);pan(S,cx);S.st.forEach(s=>{const k=prog(t,s.t0,s.t0+.55);const x=s.x0+(s.x1-s.x0)*k,y=s.y0+(s.y1-s.y0)*k-Math.sin(k*Math.PI)*260;s.e.style.left=(x+cx*.6)+'px';s.e.style.top=y+'px';s.e.style.opacity=k>0?1:0;s.e.style.transform=`rotate(${k*400}deg)`})});
// 17 AZUL DA PRÚSSIA
SC(53.7,57.8,S=>{plate(S,L('lab').room,.5);plate(S,L('lab').mesa,.8);const p=PT('lab').pote;S.t=tagAt(S,'<span class="chip" style="background:#0b3c6e"></span>AZUL DA PRÚSSIA',p[0]+60,p[1]-120,.8)},(S,t,T)=>{pan(S,kf(t,[[0,-25],[4.1,25]]));popTag(S.t,T,56.5)});
// 18 ABADIA DE GOIÁS — 300 ANOS
SC(57.8,62.2,S=>{plate(S,L('aterro').bg,.5);const p=PT('aterro').morro;S.t=tagAt(S,'ABADIA DE GOIÁS',p[0],p[1]-60,.5)},(S,t,T)=>{pan(S,kf(t,[[0,40],[4.4,-40]]));popTag(S.t,T,58.4)});
// 19 FINAL — 19 gramas, três séculos
SC(62.2,DURATION0,S=>{plate(S,L('fim').bg,.5);plate(S,L('fim').glow,.5);const p=PT('fim').po;S.g=glow(S,p[0],p[1],380,.5)},
 (S,t,T)=>{pan(S,kf(t,[[0,-30],[4.5,30]]));S.g.e.style.opacity=(.75+.2*Math.sin(T*5))*(1-prog(T,65.6,66.6))});
"""
HUD = r"""
const HUDS=[[0.25,2.4,'PÓ AZUL',T=>Math.round(19*eout(prog(T,.3,1.3)))+' g'],[2.9,6.3,'LIXO RADIOATIVO',T=>(Math.round(6000*eout(prog(T,3.0,4.6)))).toLocaleString('pt-BR')+' t'],
 [44.9,48.0,'PESSOAS EXAMINADAS',T=>(Math.round(112800*eout(prog(T,45.0,46.8)))).toLocaleString('pt-BR')],[60.0,62.1,'GUARDADO POR',T=>'300 ANOS'],
 [62.3,63.8,'CÉSIO-137',T=>'19 g'],[63.9,66.5,'VIGIADO POR',T=>'3 SÉCULOS']];
function hud(T){const h=document.getElementById('hud');let a=0,tag='',num='';for(const [a0,a1,tg,f] of HUDS){if(T>=a0&&T<a1){tag=tg;num=f(T);a=Math.min(prog(T,a0,a0+.3),1-prog(T,a1-.25,a1))}}
  h.style.opacity=a;document.getElementById('hudTag').textContent=tag;document.getElementById('hudNum').textContent=num;h.style.transform=`scale(${a>0?eback(Math.min(1,a)):1})`;
  // mostrador do detector (cena do físico)
  const g=document.getElementById('gauge');const on=(T>=33.2&&T<36.9)||(T>=37.5&&T<39.0);const a2=T<37?Math.min(prog(T,33.2,33.5),1-prog(T,36.6,36.9)):Math.min(prog(T,37.5,37.8),1-prog(T,38.75,39.0));g.style.opacity=on?a2:0;
  const k=T<37?eout(prog(T,33.5,34.6)):eout(prog(T,37.7,38.3));const ang=-70+140*k+(k>.98?Math.sin(T*55)*4:0);document.getElementById('needle').setAttribute('transform',`rotate(${ang} 250 290)`);
  document.getElementById('gmax').style.opacity=k>.98?(Math.sin(T*18)>0?1:.3):0;document.getElementById('glabel').textContent=T<37?'DETECTOR 1':'DETECTOR 2'}
"""
TAIL = TAIL0
TAIL = TAIL[:TAIL.index('function hud(T)')] + HUD + TAIL[TAIL.index('const XF=.35;'):]
TAIL = TAIL.replace("document.getElementById('fade').style.opacity=prog(T,74.4,75.5);", "document.getElementById('fade').style.opacity=prog(T,DURATION0-1.0,DURATION0-.1);")
TAIL = TAIL.replace("window.DURATION=PB[9][1];", "window.DURATION=DURATION0;")
GAUGE = """<svg id="gauge" viewBox="0 0 500 330"><rect x="10" y="10" width="480" height="310" rx="40" fill="#f6efe0" stroke="#14110f" stroke-width="12"/>
<path d="M 90 290 A 160 160 0 0 1 410 290" fill="none" stroke="#d9cfbd" stroke-width="34"/><path d="M 330 152 A 160 160 0 0 1 410 290" fill="none" stroke="#e8483a" stroke-width="34"/>
<g id="needle"><line x1="250" y1="290" x2="250" y2="120" stroke="#14110f" stroke-width="12" stroke-linecap="round"/></g><circle cx="250" cy="290" r="22" fill="#14110f"/>
<text id="gmax" x="250" y="230" text-anchor="middle" font-family="RB" font-weight="900" font-size="64" fill="#e8483a">MÁX!</text>
<text id="glabel" x="250" y="72" text-anchor="middle" font-family="RB" font-weight="900" font-size="40" letter-spacing="4" fill="#14110f">DETECTOR 1</text></svg>"""
html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div id="ov" style="position:absolute;inset:0;z-index:10;pointer-events:none"><div id="vig"></div><div id="grain"></div><div id="hud"><div id="hudTag"></div><div id="hudNum"></div></div>{GAUGE}<div id="cap"></div><div id="fade"></div></div>
<script>const DURATION0={DUR};
{JS.replace('__MAN__', json.dumps(MAN, ensure_ascii=False)).replace('__LINES__', json.dumps(TM['lines'], ensure_ascii=False)).replace('__ACT__', json.dumps(ACT))}
{SCENES_JS}
{TAIL}</script></body></html>"""
html = html.replace("file:///home/claude/holanda/noise.png", "file:///home/claude/cesio/noise.png")
open(f'{D}/ep3.html', 'w').write(html); print('ok', DUR)
