"""Monta ep2.html (episódio 2 v3) a partir de ep2/manifest.json e papi_timing.json"""
import json, os
from PIL import Image, ImageFilter
D = '/home/claude/holanda'; A = f'{D}/ep2'
MAN = json.load(open(f'{A}/manifest.json')); TM = json.load(open(f'{D}/papi_timing.json'))
# cópias desfocadas dos mapas (efeito miniatura nas bordas)
for k in ['mapa_caribe', 'mapa_atlantico']:
    if not os.path.exists(f'{A}/{k}_blur.jpg'):
        Image.open(f'{A}/{k}.png').convert('RGB').filter(ImageFilter.GaussianBlur(14)).save(f'{A}/{k}_blur.jpg', quality=90)
    if not os.path.exists(f'{A}/{k}.jpg'):
        Image.open(f'{A}/{k}.png').convert('RGB').save(f'{A}/{k}.jpg', quality=93)
CSS = r"""
@font-face{font-family:RB;src:url('file:///usr/share/fonts/truetype/google-fonts/ofl/roboto/Roboto[wdth,wght].ttf');font-weight:100 900;font-stretch:75% 100%}
@font-face{font-family:SERIF;src:url('file:///usr/share/fonts/truetype/google-fonts/ofl/cardo/Cardo-Bold.ttf')}
@font-face{font-family:CHALK;src:url('file:///usr/share/fonts/truetype/google-fonts/ofl/comicrelief/ComicRelief-Bold.ttf')}
html,body{margin:0;background:#000;width:1080px;height:1920px;overflow:hidden}
.sc{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:hidden;display:none;background:#000}
.sc img{position:absolute;display:block;max-width:none}
.abs{position:absolute}
#vig{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 45%,rgba(0,0,0,0) 55%,rgba(0,0,0,.38) 100%);pointer-events:none}
#grain{position:absolute;inset:0;background:url('file:///home/claude/holanda/noise.png');opacity:.06;mix-blend-mode:overlay}
#fade{position:absolute;inset:0;background:#000;opacity:0}
#cap{position:absolute;left:90px;right:90px;top:1440px;text-align:center;font-family:RB;font-weight:800;font-stretch:88%;font-size:74px;line-height:1.12;color:#fff;letter-spacing:.2px}
#cap span{display:inline;-webkit-text-stroke:7px rgba(12,10,8,.92);paint-order:stroke fill;text-shadow:0 4px 14px rgba(0,0,0,.55)}
#cap span.h{color:#ffd043;text-transform:uppercase;font-weight:900}
#cap span.r{color:#ff7a5c;text-transform:uppercase;font-weight:900}
.tag{position:absolute;transform:translate(-50%,-100%);font-family:RB;font-weight:900;font-stretch:80%;color:#1b1510;background:#fffaf0;border-radius:22px;padding:10px 26px;font-size:46px;letter-spacing:2px;white-space:nowrap;box-shadow:0 8px 0 rgba(20,15,10,.35),0 14px 30px rgba(0,0,0,.25)}
.tag small{font-size:34px;color:#c0392b;margin-left:10px}
.land{position:absolute;transform:translate(-50%,-50%);font-family:RB;font-weight:900;font-stretch:80%;font-size:54px;letter-spacing:8px;color:rgba(255,255,255,.92);-webkit-text-stroke:6px rgba(40,30,20,.55);paint-order:stroke fill;white-space:nowrap}
.bub{position:absolute;transform:translate(-50%,-100%);padding:20px 34px;border-radius:40px;background:#fff;font-family:RB;font-weight:900;font-stretch:84%;font-size:58px;color:#14110f;white-space:nowrap;box-shadow:0 10px 24px rgba(0,0,0,.25)}
.bub:after{content:'';position:absolute;left:var(--tx,40%);bottom:-26px;border-left:20px solid transparent;border-right:20px solid transparent;border-top:30px solid #fff}
#hud{position:absolute;left:0;right:0;top:230px;text-align:center;font-family:RB;font-stretch:75%;color:#fff;opacity:0}
#hudTag{display:inline-block;font-weight:900;font-size:44px;letter-spacing:4px;padding:10px 28px;border-radius:16px;background:#ffc531;color:#1b1510;box-shadow:0 8px 0 rgba(20,15,10,.6)}
#hudNum{font-weight:900;font-size:170px;line-height:1;margin-top:18px;-webkit-text-stroke:14px #14110f;paint-order:stroke fill;text-shadow:0 10px 20px rgba(0,0,0,.4)}
"""
JS = r"""
const MAN=__MAN__;const LINES=__LINES__;const PB=__PB__;
const A='file:///home/claude/holanda/ep2/';const M=110;
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));const prog=(t,a,b)=>clamp((t-a)/(b-a),0,1);
const ease=x=>x<.5?2*x*x:1-Math.pow(-2*x+2,2)/2;const eout=x=>1-Math.pow(1-x,3);
const eback=x=>{const c1=1.70158,c3=c1+1;return 1+c3*Math.pow(x-1,3)+c1*Math.pow(x-1,2)};
function kf(t,keys){if(t<=keys[0][0])return keys[0][1];for(let i=1;i<keys.length;i++){if(t<=keys[i][0]){const[a,va]=keys[i-1],[b,vb]=keys[i];return va+(vb-va)*ease((t-a)/(b-a))}}return keys[keys.length-1][1]}
const SCENES=[];
function scene(t0,t1,build,update){const el=document.createElement('div');el.className='sc';document.body.insertBefore(el,document.getElementById('ov'));const S={t0,t1,el,items:[]};build(S);S.update=update;SCENES.push(S);return S}
function img(S,src,x,y,par,extra={}){const e=document.createElement('img');e.src=A+src;e.style.left=x+'px';e.style.top=y+'px';Object.assign(e.style,extra);S.el.appendChild(e);const it={e,x,y,par};S.items.push(it);return it}
function layer(S,L,par){return img(S,L.src,-M,0,par??L.par)}
function frames(S,list,x,y,par,extra={}){const its=list.map((f,i)=>{const it=img(S,f,x,y,par,extra);it.e.style.visibility=i?'hidden':'visible';return it});const g={its,cur:0,set(i){if(i===this.cur)return;this.its[this.cur].e.style.visibility='hidden';this.its[i].e.style.visibility='visible';this.cur=i}};return g}
function sprite(S,sp,extra={}){const keys=Object.keys(sp.frames);const g=frames(S,keys.map(k=>sp.frames[k]),sp.x-M,sp.y,sp.par,extra);g.keys=keys;g.pick=function(k){const i=this.keys.indexOf(k);this.set(i<0?0:i)};return g}
function div(S,cls,html,x,y,par=1){const e=document.createElement('div');e.className=cls;e.innerHTML=html;e.style.left=x+'px';e.style.top=y+'px';S.el.appendChild(e);const it={e,x,y,par,isDiv:1};S.items.push(it);return it}
function placeAll(S,camX){S.items.forEach(it=>{it.e.style.transform=(it.isDiv?'translate(-50%,-100%) ':'')+(it.extra||'');it.e.style.left=(it.x+(it.dx||0)+camX*it.par)+'px';if(it.dy!==undefined)it.e.style.top=(it.y+it.dy)+'px'})}
function shift(g,dx,dy){g.its.forEach(it=>{it.dx=dx;it.dy=dy})}
function walkIn(g,t,t0,t1,dist,seed){const k=prog(t,t0,t1);shift(g,-dist*(1-eout(k)),k<1?-Math.abs(Math.sin(t*9))*8:0);if(k<1)g.pick('k'+(Math.floor(t*10+seed)%8));else happy(g,t,seed)}
// ---- comportamentos dos bonecos
function blinkK(t,seed){const p=3.1+seed*.7;return ((t+seed*1.3)%p)<.13}
function happy(g,t,seed){g.pick(blinkK(t,seed)?'blink':'base')}
function talk(g,t,on,seed){if(on){const k=Math.floor(t*7.5+seed*3);g.pick((k*7919%5)<3?'open':'base')}else g.pick(blinkK(t,seed)&&g.keys.includes('blink')?'blink':'base')}
function wave(g,t,talking){const i=Math.floor(t*9)%6;let k='w'+i;if(talking&&(Math.floor(t*7.5)*7919%5)<3&&g.keys.includes(k+'o'))k+='o';g.pick(k)}
function pop(it,T,a,b){const p=b===undefined?prog(T,a,a+.3):Math.min(prog(T,a,a+.3),1-prog(T,b-.25,b));it.e.style.opacity=p;it.extra=` scale(${p>0?eback(Math.min(1,p)):0.01})`;}
// ---- homografia (CSS matrix3d) de um retângulo w×h para 4 pontos
function homog(w,h,q){const [x0,y0]=q[0],[x1,y1]=q[1],[x2,y2]=q[2],[x3,y3]=q[3];
  const dx1=x1-x2,dx2=x3-x2,dy1=y1-y2,dy2=y3-y2,sx=x0-x1+x2-x3,sy=y0-y1+y2-y3;const det=dx1*dy2-dx2*dy1;
  const g=(sx*dy2-dx2*sy)/det,hh=(dx1*sy-sx*dy1)/det;
  const a=x1-x0+g*x1,b=x3-x0+hh*x3,c=x0,d=y1-y0+g*y1,e=y3-y0+hh*y3,f=y0;
  return `matrix3d(${a/w},${d/w},0,${g/w},${b/h},${e/h},0,${hh/h},0,0,1,0,${c},${f},0,1)`}
"""
SCENES_JS = r"""
const P=MAN.park,C=MAN.cais,SL=MAN.sala,CB=MAN.caribe,AT=MAN.atl;
function parkScene(t0,t1,tag,spr,camKeys,upd,warm){return scene(t0,t1,S=>{const L=P.layers[tag];
  layer(S,L.sky);S.wh=frames(S,L.wheel.frames,-M,0,L.wheel.par);layer(S,L.far);layer(S,L.near);
  S.g={};spr.forEach(([k,ex])=>{S.g[k]=sprite(S,P.sprites[tag][k],ex||{})});layer(S,L.fg);
  if(warm)S.el.style.filter='saturate(1.08) contrast(1.03)';
},(S,t,T)=>{upd(S,t,T);placeAll(S,kf(t,camKeys));S.wh.set(Math.floor(T*7.6)%16)})}
// 0a GANCHO — só o parque (plano de abertura)
parkScene(PB[0][0],3.71,'E',[],[[0,60],[3.71,-20]],(S,t,T)=>{});
// 0b as pessoas no parque
parkScene(3.71,PB[0][1],'A',[['mae'],['filha'],['guia']],[[0,40],[5,-40]],(S,t,T)=>{walkIn(S.g.mae,t,0,3.2,720,0);walkIn(S.g.filha,t,.2,3.4,760,3);happy(S.g.guia,t,2)});
// 1 BON BINI — ombro da mãe, guia acenando e falando
parkScene(PB[1][0],12.9,'B',[['guia'],['mae',{filter:'blur(7px)'}]],[[0,-45],[7.5,45]],(S,t,T)=>{if(T>10.35&&T<12.1)wave(S.g.guia,T,T>10.5&&T<11.2);else talk(S.g.guia,t,false,1);S.g.mae.its[0].par=1.5});
// 1b a filha olha a roda-gigante e pula de alegria
parkScene(12.9,PB[1][1],'C',[['filha']],[[0,-35],[3.3,35]],(S,t,T)=>{const j=Math.abs(Math.sin(t*5.2));S.g.filha.pick(j>.45?'up':'mid');shift(S.g.filha,0,-j*38)});
// 2 MAPA DO CARIBE (varredura lateral Aruba -> Curaçao -> Bonaire)
scene(PB[2][0],PB[2][1],S=>{S.map=img(S,CB.src.replace('.png','.jpg'),0,0,0);S.bl=img(S,'mapa_caribe_blur.jpg',0,0,0,{webkitMaskImage:'linear-gradient(to bottom,#000 0%,rgba(0,0,0,0) 30%,rgba(0,0,0,0) 62%,#000 92%)'});
  const L=CB.labels;S.la=div(S,'tag','ARUBA',L.aruba[0],L.aruba[1]-40,0);S.lc=div(S,'tag','CURAÇAO',L.curacao[0],L.curacao[1]-40,0);S.lb=div(S,'tag','BONAIRE',L.bonaire[0],L.bonaire[1]-40,0);
  S.lv=div(S,'land','VENEZUELA',L.venezuela[0]+250,L.venezuela[1]-420,0);S.lv.e.style.transform='translate(-50%,-50%)';
},(S,t,T)=>{const X=CB.xs;const c0=kf(T,[[16.17,X.aruba-60],[20.6,X.aruba+330],[22.3,X.curacao],[23.6,X.curacao+120],[25.3,X.bonaire-80]]);const c=clamp(c0,540,CB.W-540);const off=540-c;
  S.items.forEach(it=>{it.e.style.left=(it.x+off)+'px'});
  pop(S.la,T,16.6);pop(S.lc,T,22.2);pop(S.lb,T,23.3);
  [S.la,S.lc,S.lb].forEach(it=>it.e.style.transform='translate(-50%,-100%)'+it.extra);S.lv.e.style.opacity=prog(T,17,17.6)});
// 3 CAIS DE WILLEMSTAD — "bon dia, kon ta bai?"
scene(PB[3][0],PB[3][1],S=>{const L=C.layers.A,Sp=C.sprites.A;layer(S,L.far);layer(S,L.near);S.g={};['senhor','local','filha'].forEach(k=>S.g[k]=sprite(S,Sp[k]));layer(S,L.fg);
  const l=Sp.local;S.b=div(S,'bub','Bon dia, kon ta bai?',l.x-M+l.w*.62,l.y+l.h*.08,.8);S.b.e.style.setProperty('--tx','22%');
},(S,t,T)=>{placeAll(S,kf(t,[[0,45],[4.6,-45]]));talk(S.g.local,t,T>26.9&&T<28.6,0);happy(S.g.filha,t,2);pop(S.b,T,26.95);S.b.e.style.transform='translate(-50%,-100%)'+S.b.extra});
// 4/5 ATLÂNTICO
function atlScene(t0,t1,route,camK,labels,shipK){return scene(t0,t1,S=>{S.map=img(S,'mapa_atlantico.jpg',0,0,0);S.bl=img(S,'mapa_atlantico_blur.jpg',0,0,0,{webkitMaskImage:'linear-gradient(to bottom,#000 0%,rgba(0,0,0,0) 28%,rgba(0,0,0,0) 66%,#000 94%)'});
  const pts=AT[route];const d='M'+pts.map(p=>p[0].toFixed(1)+','+p[1].toFixed(1)).join(' L');
  const sv=document.createElementNS('http://www.w3.org/2000/svg','svg');sv.setAttribute('width',AT.W);sv.setAttribute('height',1920);sv.style.position='absolute';sv.style.left='0';sv.style.top='0';
  sv.innerHTML=`<path d="${d}" fill="none" stroke="rgba(0,0,0,.25)" stroke-width="12" stroke-linecap="round" stroke-dasharray="26 22" transform="translate(3,6)"/><path id="r" d="${d}" fill="none" stroke="#fff6dc" stroke-width="10" stroke-linecap="round" stroke-dasharray="26 22"/>`;
  S.el.appendChild(sv);S.items.push({e:sv,x:0,y:0,par:0});S.path=sv.querySelector('#r');S.shadowPath=sv.querySelector('path');S.len=S.path.getTotalLength();
  S.mask=document.createElementNS('http://www.w3.org/2000/svg','mask');
  S.ship=img(S,'barco_c.png',0,0,0,{width:'150px'});S.labs=labels.map(([k,txt,cls])=>{const p=AT.labels[k];const it=div(S,cls||'tag',txt,p[0],p[1]-(cls?0:30),0);if(cls)it.e.style.transform='translate(-50%,-50%)';return it});
},(S,t,T)=>{const c=clamp(kf(T,camK),540,AT.W-540);const off=540-c;S.items.forEach(it=>{it.e.style.left=(it.x+off)+'px'});
  const k=prog(T,shipK[0],shipK[1]);const kk=ease(k);const L=S.len*kk;
  // revela a rota até o barco
  S.path.setAttribute('stroke-dasharray',`${'26 22 '.repeat(Math.ceil(L/48)).trim()} 0 ${S.len*2}`);S.shadowPath.setAttribute('stroke-dasharray',S.path.getAttribute('stroke-dasharray'));
  const p=S.path.getPointAtLength(L),q=S.path.getPointAtLength(Math.min(S.len,L+4));const dir=q.x<p.x?-1:1;
  S.ship.x=p.x-75;S.ship.y=p.y-110+Math.sin(T*3)*4;S.ship.e.style.top=S.ship.y+'px';S.ship.e.style.left=(S.ship.x+off)+'px';S.ship.e.style.transform=`scaleX(${-dir})`;S.ship.e.style.opacity=k>0&&k<1.01?1:0;
  S.labs.forEach((it,i)=>{const a=labels[i][3];if(labels[i][2]){it.e.style.opacity=prog(T,a,a+.4)}else{pop(it,T,a);it.e.style.transform='translate(-50%,-100%)'+it.extra}})})}
const ax=k=>AT.labels[k][0];
atlScene(PB[4][0],PB[4][1],'rotaAfrica',[[30.24,ax('africa')-60],[31.6,ax('africa')-120],[35.8,ax('caribe')+180]],[['africa','ÁFRICA','land',30.5],['caribe','CARIBE','land',34.6],['brasil','BRASIL','land',30.5]],[31.0,35.6]);
atlScene(PB[5][0],PB[5][1],'rotaRecife',[[36.02,ax('recife')+40],[38.8,ax('recife')-40],[42.6,ax('curacao')+150]],[['recife','RECIFE<small>1654</small>',null,37.8],['curacao','CURAÇAO',null,42.3],['brasil','BRASIL','land',36.1]],[38.9,42.5]);
// 6 O LIVRO TRANCADO
scene(PB[6][0],PB[6][1],S=>{const L=SL.layers.K;layer(S,L.room);layer(S,L.desk);
  const w=600,h=200;S.tx=div(S,'abs',`<div style="width:${w}px;height:${h}px;display:flex;align-items:center;justify-content:center;font-family:SERIF;font-size:92px;letter-spacing:6px;color:#e9c46a;text-shadow:0 2px 0 #7a5a1a,0 -1px 0 #fff3c0">NEDERLANDS</div>`,-M,0,.8);
  S.tx.e.style.transformOrigin='0 0';const q=SL.cover.map(p=>[p[0],p[1]]);S.tx.m=homog(w,h,q);S.tx.isDiv=0;
  S.el.style.filter='saturate(.9)';
},(S,t,T)=>{const cx=kf(t,[[0,30],[5.6,-30]]);S.items.forEach(it=>{it.e.style.left=(it.x+cx*it.par)+'px'});S.tx.e.style.transform=S.tx.m;});
// 7 SALA DE AULA
scene(PB[7][0],PB[7][1],S=>{const L=SL.layers.W,Sp=SL.sprites;layer(S,L.room);
  const w=900,h=300;S.tx=div(S,'abs',`<div style="width:${w}px;height:${h}px;display:flex;flex-direction:column;align-items:center;justify-content:center;font-family:CHALK;font-size:84px;line-height:1.1;color:rgba(245,245,235,.9);text-shadow:0 0 3px rgba(255,255,255,.5)">ALLEEN<br>NEDERLANDS</div>`,-M,0,.45);
  S.tx.e.style.transformOrigin='0 0';S.tx.m=homog(w,h,SL.board);S.tx.isDiv=0;
  S.g={};S.g.canto=sprite(S,Sp.canto);S.g.prof=sprite(S,Sp.prof);layer(S,L.desk);['a1','a2','a3'].forEach(k=>S.g[k]=sprite(S,Sp[k]));layer(S,L.fg);
  const a=Sp.a2;S.b=div(S,'bub','Bon dia!',a.x-M+a.w*.5,a.y+a.h*.12,a.par);
  const c=Sp.canto;S.x=div(S,'abs','<div style="font-family:RB;font-weight:900;font-size:120px;color:#e8483a;-webkit-text-stroke:8px #fff;paint-order:stroke fill">✕</div>',c.x-M+c.w*.55,c.y+c.h*.2,c.par);
},(S,t,T)=>{const cx=kf(t,[[0,40],[7.1,-40]]);S.items.forEach(it=>{it.e.style.left=(it.x+cx*it.par)+'px'});S.tx.e.style.transform=S.tx.m;
  talk(S.g.prof,t,T>48.7&&T<52.4,0);pop(S.b,T,52.75,54.4);S.b.e.style.transform='translate(-50%,-100%)'+S.b.extra;pop(S.x,T,54.9);S.x.e.style.transform='translate(-50%,-100%)'+S.x.extra});
// 8 HOJE — Curaçao fala papiamento
scene(PB[8][0],PB[8][1],S=>{const L=C.layers.B,Sp=C.sprites.B;layer(S,L.far);layer(S,L.near);S.g={};['local','senhor','moca','rapaz','menino'].forEach(k=>S.g[k]=sprite(S,Sp[k]));layer(S,L.fg);
},(S,t,T)=>{placeAll(S,kf(t,[[0,-50],[10.3,50]]));talk(S.g.moca,t,(t%3.2)<1.6,0);happy(S.g.rapaz,t,1);talk(S.g.local,t,((t+1.6)%3.2)<1.6,2);happy(S.g.senhor,t,3);wave(S.g.menino,t,false)});
// 9 FINAL — pôr do sol no parque, todos dando tchau
parkScene(PB[9][0],PB[9][1],'S',[['mae',{filter:'sepia(.18) saturate(1.1) brightness(.97)'}],['filha',{filter:'sepia(.18) saturate(1.1) brightness(.97)'}],['guia',{filter:'sepia(.18) saturate(1.1) brightness(.97)'}]],[[0,50],[9.6,-50]],(S,t,T)=>{const w=T>72.55;if(w){wave(S.g.mae,T+.3);wave(S.g.filha,T);wave(S.g.guia,T+.6)}else{happy(S.g.mae,t,0);happy(S.g.filha,t,1);happy(S.g.guia,t,2)}},true);
"""
TAIL = r"""
// ---------- legendas
const CHUNKS=[];
LINES.forEach(([a,b,txt,wt])=>{
  const toks=txt.split(' ');let mode='';const words=toks.map(tk=>{let k=mode;if(tk.startsWith('*')){k='h';tk=tk.slice(1)}if(tk.startsWith('~')){k='r';tk=tk.slice(1)}let end=false;const mm=tk.match(/^(.*?)[*~]([.,?!…]*)$/);if(mm){end=true;tk=mm[1]+mm[2]} mode=end?'':k;return{t:tk,k}});
  words.forEach((w,i)=>{w.at=wt[i]});
  let cur=[];const flush=()=>{if(cur.length)CHUNKS.push(cur);cur=[]};
  words.forEach((w,i)=>{cur.push(w);const len=cur.reduce((s,x)=>s+x.t.length+1,0);const brk=/[.,?!…]$/.test(w.t);if(len>26||(brk&&len>8)||/[?!.…]$/.test(w.t))flush()});flush();
});
CHUNKS.forEach((c,i)=>{c.t0=c[0].at;c.t1=i+1<CHUNKS.length?Math.min(CHUNKS[i+1][0].at,c[c.length-1].at+1.6):c[c.length-1].at+1.6});
let curChunk=null;const capEl=document.getElementById('cap');
function updCaps(T){const c=CHUNKS.find(c=>T>=c.t0&&T<c.t1)||null;
  if(c!==curChunk){curChunk=c;capEl.innerHTML=c?c.map(w=>`<span class="${w.k}">${w.t}</span>`).join(' '):''}
  if(c){const p=prog(T,c.t0,c.t0+.12),q=1-prog(T,c.t1-.08,c.t1);capEl.style.opacity=Math.min(p,q);capEl.style.transform=`translateY(${(1-eout(p))*10}px)`}else capEl.style.opacity=0}
function hud(T){const h=document.getElementById('hud');let tag='',num='',a=0;
  if(T>=57.4&&T<60.5){tag='FALAM PAPIAMENTO';num=Math.round(80*eout(prog(T,57.6,58.8)))+'%';a=Math.min(prog(T,57.4,57.7),1-prog(T,60.2,60.5))}
  else if(T>=62.3&&T<64.3){tag='OFICIAL EM ARUBA';num='2003';a=Math.min(prog(T,62.3,62.6),1-prog(T,64.0,64.3))}
  else if(T>=64.3&&T<65.96){tag='OFICIAL EM CURAÇAO';num='2007';a=Math.min(prog(T,64.3,64.6),1-prog(T,65.7,65.96))}
  h.style.opacity=a;document.getElementById('hudTag').textContent=tag;document.getElementById('hudNum').textContent=num;h.style.transform=`scale(${a>0?eback(a):1})`}
const XF=.35;
window.setT=function(T){
  SCENES.forEach((S,i)=>{const on=T>=S.t0&&T<S.t1+XF;S.el.style.display=on?'block':'none';
    if(on){S.update(S,T-S.t0,T);const next=SCENES[i+1];S.el.style.opacity=next&&T>=S.t1?1-prog(T,S.t1,S.t1+XF):1;S.el.style.zIndex=(next&&T>=S.t1)?3:2}});
  document.getElementById('grain').style.backgroundPosition=`${(T*977)%512}px ${(T*613)%512}px`;
  document.getElementById('fade').style.opacity=prog(T,74.4,75.5);
  updCaps(T);hud(T)};
window.SCENE_BOUNDS=SCENES.map(s=>[s.t0,s.t1]);window.DURATION=PB[9][1];
"""
bounds = TM['bounds']
html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div id="ov" style="position:absolute;inset:0;z-index:10;pointer-events:none"><div id="vig"></div><div id="grain"></div><div id="hud"><div id="hudTag"></div><div id="hudNum"></div></div><div id="cap"></div><div id="fade"></div></div>
<script>{JS.replace('__MAN__', json.dumps(MAN, ensure_ascii=False)).replace('__LINES__', json.dumps(TM['lines'], ensure_ascii=False)).replace('__PB__', json.dumps(bounds))}
{SCENES_JS}
{TAIL}</script></body></html>"""
open(f'{D}/ep2.html', 'w').write(html); print('ok', bounds[-1])
