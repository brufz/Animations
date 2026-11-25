// Elenco 3D: carrega personagens com esqueleto, troca cores das roupas e aplica animações de outra fonte (mesmo padrão de ossos Mixamo)
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {DRACOLoader} from 'three/addons/loaders/DRACOLoader.js';
const draco=new DRACOLoader();draco.setDecoderPath('./examples/jsm/libs/draco/gltf/');
const gl=new GLTFLoader();gl.setDRACOLoader(draco);
const M='examples/models/gltf/';
let MOTION=null;
const key=n=>n.replace(/^mixamorig:?/,'').replace(/^.*:/,'');
export async function motions(){
  if(MOTION)return MOTION;MOTION={};
  for(const f of ['Xbot.glb','Soldier.glb','Michelle.glb']){const g=await gl.loadAsync(M+f);let sk=null;g.scene.traverse(o=>{if(o.isSkinnedMesh&&!sk)sk=o.skeleton});
    g.animations.forEach(a=>{MOTION[(f.split('.')[0]+':'+a.name).toLowerCase()]={clip:a,root:g.scene,skel:sk}})}
  return MOTION;}
// retarget em espaço de mundo: rotação do osso relativa à pose de repouso da fonte, aplicada à pose de repouso do alvo
function tposeFix(sk,root){
  for(const side of ['Left','Right']){
    for(const seg of [['Arm','ForeArm'],['ForeArm','Hand']]){
      const a=sk.bones.find(b=>key(b.name)===side+seg[0]),c=sk.bones.find(b=>key(b.name)===side+seg[1]);if(!a||!c)continue;
      root.updateMatrixWorld(true);const pa=a.getWorldPosition(new THREE.Vector3()),pc=c.getWorldPosition(new THREE.Vector3());
      const d=pc.sub(pa).normalize();const rw=new THREE.Quaternion();root.getWorldQuaternion(rw);
      // direção horizontal desejada no espaço do personagem
      const want=new THREE.Vector3(d.x>=0?1:-1,0,0).applyQuaternion(rw);want.y=0;want.normalize();
      const q=new THREE.Quaternion().setFromUnitVectors(d,want);
      const wq=a.getWorldQuaternion(new THREE.Quaternion());const nw=q.multiply(wq);
      const pw=a.parent.getWorldQuaternion(new THREE.Quaternion());a.quaternion.copy(pw.invert().multiply(nw));
    }}
  root.updateMatrixWorld(true);}
function snapRest(sk){sk.bones.forEach(b=>{if(!b.userData.r)b.userData.r=[b.position.clone(),b.quaternion.clone(),b.scale.clone()]})}
function rest(sk){sk.bones.forEach(b=>{const r=b.userData.r;b.position.copy(r[0]);b.quaternion.copy(r[1]);b.scale.copy(r[2])})}
export function retarget(src,root,fps=30){
  const {clip,root:sroot,skel:sskel}=src;
  let tsk=null;root.traverse(o=>{if(o.isSkinnedMesh&&!tsk)tsk=o.skeleton});
  const sb={};sskel.bones.forEach(b=>sb[key(b.name)]=b);
  const tb=tsk.bones;snapRest(sskel);snapRest(tsk);
  // poses de repouso
  rest(sskel);sroot.updateMatrixWorld(true);const sRest={};for(const k in sb)sRest[k]=sb[k].getWorldQuaternion(new THREE.Quaternion());
  rest(tsk);root.updateMatrixWorld(true);tposeFix(tsk,root);
  const tRestW=new Map(),tRestL=new Map();tb.forEach(b=>{tRestW.set(b,b.getWorldQuaternion(new THREE.Quaternion()));tRestL.set(b,b.quaternion.clone())});
  const rootW=n=>{const q=new THREE.Quaternion();if(n.parent)n.parent.getWorldQuaternion(q);return q};
  const tParentRest=new Map();tb.forEach(b=>tParentRest.set(b,rootW(b)));
  const mx=new THREE.AnimationMixer(sroot);mx.clipAction(clip).play();
  const n=Math.max(2,Math.round(clip.duration*fps));const times=[];const vals=new Map();tb.forEach(b=>vals.set(b,[]));
  for(let i=0;i<n;i++){const t=i/(n-1)*clip.duration;times.push(t);mx.setTime(t);sroot.updateMatrixWorld(true);
    const W=new Map();
    for(const b of tb){const k=key(b.name);let pw=(b.parent&&b.parent.isBone&&W.has(b.parent))?W.get(b.parent):tParentRest.get(b);
      let w;if(sb[k]){const d=sb[k].getWorldQuaternion(new THREE.Quaternion()).multiply(sRest[k].clone().invert());w=d.multiply(tRestW.get(b));}
      else w=pw.clone().multiply(tRestL.get(b));
      W.set(b,w);const l=pw.clone().invert().multiply(w);vals.get(b).push(l.x,l.y,l.z,l.w);}}
  mx.stopAllAction();rest(sskel);rest(tsk);
  const tracks=tb.map(b=>new THREE.QuaternionKeyframeTrack(b.name+'.quaternion',times,vals.get(b)));
  return new THREE.AnimationClip(clip.name,clip.duration,tracks);}

// ---------- edição de malha: cortar/pintar triângulos por osso, cor da textura e posição; recolorir textura; acessórios
function texData(map){if(!map||!map.image)return null;const im=map.image;const c=new OffscreenCanvas(im.width,im.height);const x=c.getContext('2d');x.drawImage(im,0,0);return {d:x.getImageData(0,0,im.width,im.height),w:im.width,h:im.height,c,x};}
function hsl(r,g,b){const c=new THREE.Color(r/255,g/255,b/255);const o={};c.getHSL(o);return o;}
function match(rule,tri){
  if(rule.bones&&!new RegExp(rule.bones).test(tri.bone))return false;
  if(rule.col){const c=rule.col,h=tri.hsl;if(c.lMax!==undefined&&h.l>c.lMax)return false;if(c.lMin!==undefined&&h.l<c.lMin)return false;if(c.sMin!==undefined&&h.s<c.sMin)return false;if(c.sMax!==undefined&&h.s>c.sMax)return false;
    if(c.h){const hh=h.h*360;const ok=c.h[0]<=c.h[1]?(hh>=c.h[0]&&hh<=c.h[1]):(hh>=c.h[0]||hh<=c.h[1]);if(!ok)return false;}}
  if(rule.far){const f=rule.far;if(tri.p.distanceTo(new THREE.Vector3(...f.c))<f.r)return false;}
  if(rule.near){const f=rule.near;if(tri.p.distanceTo(new THREE.Vector3(...f.c))>f.r)return false;}
  if(rule.yBelow!==undefined&&tri.p.y>rule.yBelow)return false;
  if(rule.yAbove!==undefined&&tri.p.y<rule.yAbove)return false;
  if(rule.absXBelow!==undefined&&Math.abs(tri.p.x)>rule.absXBelow)return false;
  if(rule.absXAbove!==undefined&&Math.abs(tri.p.x)<rule.absXAbove)return false;
  return true;}
function squash(m,ops){const g=m.geometry;const P=g.attributes.position,SI=g.attributes.skinIndex,SW=g.attributes.skinWeight;const v=new THREE.Vector3(),q=new THREE.Vector3();
  const T=(i,x)=>{v.copy(x);m.applyBoneTransform(i,v);return v.applyMatrix4(m.matrixWorld).clone();};
  for(let i=0;i<P.count;i++){let bi=0,bw=-1;for(let k=0;k<4;k++){const w=SW.getComponent(i,k);if(w>bw){bw=w;bi=SI.getComponent(i,k)}}const bn=key(m.skeleton.bones[bi].name);
    for(const op of ops){if(!new RegExp(op.bones).test(bn))continue;q.fromBufferAttribute(P,i);const p0=T(i,q);if(p0.y<op.y[0]||p0.y>op.y[1]||p0.z<=op.z0)continue;
      const tgt=new THREE.Vector3(0,0,(op.z0+(p0.z-op.z0)*op.k)-p0.z);const e=1e-3*(op.e||1);const cols=[0,1,2].map(a=>{const d=q.clone();d.setComponent(a,d.getComponent(a)+e);return T(i,d).sub(p0).multiplyScalar(1/e);});
      const L=new THREE.Matrix3().set(cols[0].x,cols[1].x,cols[2].x,cols[0].y,cols[1].y,cols[2].y,cols[0].z,cols[1].z,cols[2].z);const dl=tgt.applyMatrix3(L.invert());P.setXYZ(i,q.x+dl.x,q.y+dl.y,q.z+dl.z);break;}}
  P.needsUpdate=true;g.computeVertexNormals();}
function editMesh(m,rules,sq){
  const g=m.geometry.clone();m.geometry=g;if(sq)squash(m,sq);const P=g.attributes.position,UV=g.attributes.uv,SI=g.attributes.skinIndex,SW=g.attributes.skinWeight;
  const idx=g.index?Array.from(g.index.array):[...Array(P.count).keys()];
  const base=Array.isArray(m.material)?m.material[0]:m.material;const T=texData(base.map);
  const v=new THREE.Vector3();const mats=[base];const groups=[[]];const matOf={};
  for(let t=0;t<idx.length;t+=3){const p=new THREE.Vector3();let u=0,w=0;const bw={};
    for(let k=0;k<3;k++){const i=idx[t+k];v.fromBufferAttribute(P,i);m.applyBoneTransform(i,v);v.applyMatrix4(m.matrixWorld);p.add(v);
      if(UV){u+=UV.getX(i);w+=UV.getY(i);}for(let j=0;j<4;j++){const bi=SI.getComponent(i,j);bw[bi]=(bw[bi]||0)+SW.getComponent(i,j);}}
    p.multiplyScalar(1/3);let bb=0,bv=-1;for(const k in bw)if(bw[k]>bv){bv=bw[k];bb=+k;}
    let h={h:0,s:0,l:.5};if(T){const px=Math.min(T.w-1,Math.max(0,Math.floor(u/3*T.w))),py=Math.min(T.h-1,Math.max(0,Math.floor(w/3*T.h)));const o=(py*T.w+px)*4;h=hsl(T.d.data[o],T.d.data[o+1],T.d.data[o+2]);}
    const tri={p,bone:key(m.skeleton.bones[bb].name),hsl:h};let gi=0;
    for(const r of rules){if(!match(r,tri))continue;if(r.act==='cut'){gi=-1;break;}
      if(r.act==='paint'){const kk=r.color;if(matOf[kk]===undefined){const nm=new THREE.MeshStandardMaterial({color:new THREE.Color(r.color),roughness:r.rough??.75,metalness:0,normalMap:base.normalMap||null});mats.push(nm);groups.push([]);matOf[kk]=mats.length-1;}gi=matOf[kk];break;}}
    if(gi>=0)groups[gi].push(idx[t],idx[t+1],idx[t+2]);}
  const ni=[];g.clearGroups();let st=0;groups.forEach((gr,i)=>{if(!gr.length)return;ni.push(...gr);g.addGroup(st,gr.length,i);st+=gr.length;});
  g.setIndex(ni);m.material=mats;}
function recolorTex(m,maps){const base=Array.isArray(m.material)?m.material[0]:m.material;const T=texData(base.map);if(!T)return;const D=T.d.data;const c=new THREE.Color();const o={};
  for(let i=0;i<D.length;i+=4){c.setRGB(D[i]/255,D[i+1]/255,D[i+2]/255);c.getHSL(o);const hh=o.h*360;
    for(const r of maps){const ok=(r.h[0]<=r.h[1]?(hh>=r.h[0]&&hh<=r.h[1]):(hh>=r.h[0]||hh<=r.h[1]))&&o.s>=(r.sMin||0)&&o.l>=(r.lMin||0)&&o.l<=(r.lMax??1);
      if(ok){c.setHSL(r.to[0]/360,r.to[1]??o.s,Math.min(1,Math.max(0,o.l*(r.lMul||1)+(r.lAdd||0))));D[i]=c.r*255;D[i+1]=c.g*255;D[i+2]=c.b*255;break;}}}
  T.x.putImageData(T.d,0,0);const nt=new THREE.CanvasTexture(T.c);nt.flipY=false;nt.colorSpace=THREE.SRGBColorSpace;nt.channel=base.map.channel;base.map=nt;base.needsUpdate=true;}
function addProps(obj,props){const bones={};obj.traverse(o=>{if(o.isBone)bones[key(o.name)]=o});
  for(const p of props){const geo=p.type==='sphere'?new THREE.SphereGeometry(1,24,16,0,Math.PI*2,0,p.theta||Math.PI):p.type==='torus'?new THREE.TorusGeometry(1,p.tube||.3,10,24):p.type==='cyl'?new THREE.CylinderGeometry(p.r1??1,p.r2??1,1,24):new THREE.BoxGeometry(1,1,1);
    const mat=new THREE.MeshStandardMaterial({color:new THREE.Color(p.color),roughness:p.rough??.7,metalness:0});const me=new THREE.Mesh(geo,mat);me.castShadow=true;
    me.position.set(...p.pos);me.scale.set(...p.scale);if(p.rot)me.rotation.set(...p.rot);obj.add(me);obj.updateMatrixWorld(true);(bones[p.bone]||obj).attach(me);}}
export async function load(spec){
  const g=await gl.loadAsync(M+spec.model);const obj=g.scene;
  obj.updateMatrixWorld(true);
  if(spec.edit)obj.traverse(o=>{if(o.isSkinnedMesh&&spec.edit[o.name]){const e=spec.edit[o.name];if(e.tex){o.material=o.material.clone();recolorTex(o,e.tex);}if(e.rules||e.squash)editMesh(o,e.rules||[],e.squash);}});
  if(spec.props)addProps(obj,spec.props);
  // proporções (ex.: criança): escala por osso, aplicada antes de medir altura e do retarget
  if(spec.prop){obj.traverse(o=>{if(!o.isBone)return;const k=key(o.name).replace(/^(Left|Right)/,'');const f=spec.prop[k];if(f)o.scale.multiplyScalar(f);});}
  if(spec.only)obj.traverse(o=>{if(o.isMesh&&!o.name.startsWith(spec.only))o.visible=false});
  obj.traverse(o=>{if((o.isMesh||o.isSkinnedMesh)&&o.visible){o.castShadow=true;o.frustumCulled=false;
    if(o.material&&!Array.isArray(o.material)){o.material=o.material.clone();const c=spec.colors&&spec.colors[o.name];if(c!==undefined){if(c===null)o.visible=false;else{o.material.color=new THREE.Color(c);}}
      if(spec.tint&&spec.tint[o.name])o.material.color.multiply(new THREE.Color(spec.tint[o.name]));}}});
  const box=new THREE.Box3();obj.updateMatrixWorld(true);obj.traverse(o=>{if(o.isMesh&&o.visible)box.expandByObject(o)});const h=box.max.y-box.min.y;const s=(spec.height||1.72)/h;obj.scale.multiplyScalar(s);
  obj.updateMatrixWorld(true);const b2=new THREE.Box3();obj.traverse(o=>{if(o.isMesh&&o.visible)b2.expandByObject(o)});obj.userData.y0=-b2.min.y;
  const mx=new THREE.AnimationMixer(obj);const actions={};
  const mot=await motions();
  for(const [k,src] of Object.entries(spec.anims||{})){const clip=src.startsWith('own:')?g.animations.find(a=>a.name===src.slice(4)):retarget(mot[src.toLowerCase()],obj);
    if(clip)actions[k]={a:mx.clipAction(clip),dur:clip.duration};}
  return {obj,mx,actions,spec};}
// pose num instante: mistura de até 2 ações (peso w2 na segunda)
export function pose(A,k1,t1,k2,t2,w2){
  for(const [k,v] of Object.entries(A.actions)){v.a.enabled=false;v.a.stop();}
  const a1=A.actions[k1];a1.a.reset();a1.a.enabled=true;a1.a.setEffectiveWeight(1-(w2||0));a1.a.play();a1.a.time=t1%a1.dur;
  if(k2&&w2>0){const a2=A.actions[k2];a2.a.reset();a2.a.enabled=true;a2.a.setEffectiveWeight(w2);a2.a.play();a2.a.time=t2%a2.dur;}
  A.mx.update(0);}
