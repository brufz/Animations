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
export async function load(spec){
  const g=await gl.loadAsync(M+spec.model);const obj=g.scene;
  if(spec.only)obj.traverse(o=>{if(o.isMesh&&!o.name.startsWith(spec.only))o.visible=false});
  obj.traverse(o=>{if((o.isMesh||o.isSkinnedMesh)&&o.visible){o.castShadow=true;o.frustumCulled=false;
    if(o.material){o.material=o.material.clone();const c=spec.colors&&spec.colors[o.name];if(c!==undefined){if(c===null)o.visible=false;else{o.material.color=new THREE.Color(c);}}
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
