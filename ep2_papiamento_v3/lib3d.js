// Biblioteca comum dos cenários 3D (raymarching SDF, renderizado em camadas para parallax 2.5D)
// Cada cenário define SCENE_GLSL com: vec2 scene(vec3 p); vec3 mcol(float m,vec3 p,vec3 n,inout float ks,inout float em);
// vec3 SKY(vec3 rd); bool groundOK(vec3 p); float groundMat(vec3 p); e opcionalmente WATER (material 50 reflete).
const VS3=`#version 300 es
in vec2 p;void main(){gl_Position=vec4(p,0,1);}`;
const HEAD3=`#version 300 es
precision highp float;
uniform vec2 R;uniform vec3 camP,camT,Ldir,Lcol,Acol;uniform float span,layer,zSplit,wheelA,T,sunset,fogK,fogStart,groundY,useGround,tmaxU;
out vec4 o;
bool GR=true;bool INSH=false;
float sdCap(vec3 p,vec3 a,vec3 b,float r){vec3 pa=p-a,ba=b-a;float h=clamp(dot(pa,ba)/dot(ba,ba),0.,1.);return length(pa-ba*h)-r;}
float sdSph(vec3 p,vec3 c,float r){return length(p-c)-r;}
float sdEll(vec3 p,vec3 c,vec3 r){p-=c;float k0=length(p/r),k1=length(p/(r*r));return k0*(k0-1.)/k1;}
float sdCyl(vec3 p,vec3 c,float h,float r){p-=c;vec2 d=abs(vec2(length(p.xz),p.y))-vec2(r,h);return min(max(d.x,d.y),0.)+length(max(d,0.));}
float sdRBox(vec3 p,vec3 c,vec3 b,float r){vec3 q=abs(p-c)-b;return length(max(q,0.))+min(max(q.x,max(q.y,q.z)),0.)-r;}
float sdTorZ(vec3 p,vec3 c,vec2 t){p-=c;vec2 q=vec2(length(p.xy)-t.x,p.z);return length(q)-t.y;}
float sdTorY(vec3 p,vec3 c,vec2 t){p-=c;vec2 q=vec2(length(p.xz)-t.x,p.y);return length(q)-t.y;}
float sdCCone(vec3 p,vec3 c,float h,float r1,float r2){p-=c;vec2 q=vec2(length(p.xz),p.y);vec2 k1=vec2(r2,h),k2=vec2(r2-r1,2.*h);vec2 ca=vec2(q.x-min(q.x,(q.y<0.)?r1:r2),abs(q.y)-h);vec2 cb=q-k1+k2*clamp(dot(k1-q,k2)/dot(k2,k2),0.,1.);float s=(cb.x<0.&&ca.y<0.)?-1.:1.;return s*sqrt(min(dot(ca,ca),dot(cb,cb)));}
float smin(float a,float b,float k){float h=clamp(.5+.5*(b-a)/k,0.,1.);return mix(b,a,h)-k*h*(1.-h);}
vec2 U(vec2 a,vec2 b){return a.x<b.x?a:b;}
mat2 rot(float a){float c=cos(a),s=sin(a);return mat2(c,-s,s,c);}
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float vn(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}
`;
const MAIN3=`
vec2 map(vec3 p){return scene(p);}
vec3 nor(vec3 p,float t){vec2 e=vec2(.001+.0004*t,0);return normalize(vec3(map(p+e.xyy).x-map(p-e.xyy).x,map(p+e.yxy).x-map(p-e.yxy).x,map(p+e.yyx).x-map(p-e.yyx).x));}
float shadow(vec3 ro,vec3 rd){INSH=true;float res=1.,t=.03;for(int i=0;i<140;i++){float h=map(ro+rd*t).x;if(h<.3)res=min(res,5.*h/t);t+=clamp(h*.7,.02,.3);if(res<.002||t>30.)break;}INSH=false;res=clamp(res,0.,1.);return res*res*(3.-2.*res);}
float ao(vec3 p,vec3 n){float o=0.,s=1.;for(int i=1;i<6;i++){float h=.06*float(i);o+=(h-map(p+n*h).x)*s;s*=.6;}return clamp(1.-1.6*o,0.,1.);}
// marcha primária; devolve t e material (0 = nada)
vec2 march(vec3 ro,vec3 rd,float tmax,out float tt){
  float tp=(useGround>.5&&rd.y<0.)?(groundY-ro.y)/rd.y:1e5;
  float t=0.;vec2 h=vec2(1e3,0.);GR=false;bool hit=false;
  for(int i=0;i<420;i++){h=map(ro+rd*t);if(abs(h.x)<.0008*t+.0002){hit=true;break;}if(t>min(tmax,tp))break;t+=h.x*.85;}
  GR=true;
  if(!hit||t>=tp){ if(tp<1e4&&tp<tmax){vec3 pg=ro+rd*tp;if(groundOK(pg)){tt=tp;return vec2(0.,groundMat(pg));}} tt=1e5;return vec2(1e3,0.);}
  tt=t;return h;}
vec3 shade(vec3 ro,vec3 rd,vec3 p,vec2 h,float t,out float alpha){
  alpha=1.;vec3 n=(abs(p.y-groundY)<.002&&useGround>.5)?vec3(0,1,0):nor(p,t);
  float ks=.1,em=0.;vec3 c=mcol(h.y,p,n,ks,em);
  if(em>.5)return c;
  vec3 L=normalize(Ldir);
  GR=false;float sh=shadow(p+n*(.02+.003*t),L);GR=true;float a=ao(p,n);
  float dif=clamp(dot(n,L),0.,1.)*sh;float sky=.5+.5*n.y;
  vec3 Lb=normalize(vec3(-L.x,.4,-L.z));float back=pow(clamp(dot(n,Lb),0.,1.),2.);
  float fre=pow(1.-clamp(dot(n,-rd),0.,1.),4.);
  vec3 lin=Lcol*dif*1.2+Acol*sky*.55*a+Lcol*vec3(1.,.8,.6)*back*.3*a+vec3(.9,.8,.7)*fre*.2*a;
  vec3 res=c*lin;
  res+=Lcol*pow(clamp(dot(reflect(rd,n),L),0.,1.),ks>.5?60.:20.)*ks*sh;
  float fg=1.-exp(-max(t-fogStart,0.)*fogK);res=mix(res,SKY(normalize(vec3(rd.x,max(rd.y,.02)*.5,rd.z)))*vec3(1.,.97,.95),fg*.8);
  return res;}
vec3 tone(vec3 res){res=1.-exp(-res*1.3);float lu=dot(res,vec3(.3,.59,.11));res=mix(vec3(lu),res,1.15);return pow(max(res,0.),vec3(.95));}
void main(){
  vec2 uv=(gl_FragCoord.xy-.5*R)/R.y;
  vec3 ro=camP,ta=camT;vec3 ww=normalize(ta-ro),uu=normalize(cross(vec3(0,1,0),ww)),vv=cross(ww,uu);
  vec3 rd=normalize(uv.x*uu+uv.y*vv+span*ww);
  float t;vec2 h=march(ro,rd,tmaxU,t);
  if(h.y<.5){ if(layer>.5&&layer<1.5){o=vec4(tone(SKY(rd)),1);return;} o=vec4(0);return;}
  vec3 p=ro+rd*t;float al;vec3 res;
  if(h.y>49.5&&h.y<50.5){ // água: reflexo
    vec3 n=normalize(vec3((vn(p.xz*vec2(1.2,4.)+T*.4)-.5)*.06,1.,(vn(p.xz*vec2(1.,3.5)-T*.3+7.)-.5)*.12));
    vec3 rr=reflect(rd,n);float t2;vec2 h2=march(p+vec3(0,.01,0),rr,tmaxU,t2);
    vec3 rc=h2.y<.5?SKY(rr):shade(p,rr,p+rr*t2,h2,t2,al);
    float fr=.25+.75*pow(1.-clamp(dot(n,-rd),0.,1.),4.);
    float ks=0.,em=0.;vec3 wc=mcol(50.,p,n,ks,em);
    res=mix(wc,rc,fr*.85);
    res+=Lcol*pow(clamp(dot(reflect(rd,n),normalize(Ldir)),0.,1.),80.)*.6;
    float fg=1.-exp(-max(t-fogStart,0.)*fogK);res=mix(res,SKY(normalize(vec3(rd.x,max(rd.y,.02)*.5,rd.z))),fg*.8);
  } else res=shade(ro,rd,p,h,t,al);
  o=vec4(tone(res),1);
}`;
function make3d(sceneGLSL){
  const c=document.getElementById('c');const gl=c.getContext('webgl2',{premultipliedAlpha:false,preserveDrawingBuffer:true,alpha:true});
  function sh(t,s){const x=gl.createShader(t);gl.shaderSource(x,s);gl.compileShader(x);if(!gl.getShaderParameter(x,gl.COMPILE_STATUS))throw gl.getShaderInfoLog(x);return x}
  const pr=gl.createProgram();gl.attachShader(pr,sh(gl.VERTEX_SHADER,VS3));gl.attachShader(pr,sh(gl.FRAGMENT_SHADER,HEAD3+sceneGLSL+MAIN3));gl.linkProgram(pr);gl.useProgram(pr);
  const b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,3,-1,-1,3]),gl.STATIC_DRAW);
  const l=gl.getAttribLocation(pr,'p');gl.enableVertexAttribArray(l);gl.vertexAttribPointer(l,2,gl.FLOAT,false,0,0);
  const U=n=>gl.getUniformLocation(pr,n);
  window.draw=(o)=>{c.width=o.w;c.height=o.h;gl.viewport(0,0,o.w,o.h);gl.uniform2f(U('R'),o.w,o.h);
    gl.uniform3fv(U('camP'),o.camP);gl.uniform3fv(U('camT'),o.camT);
    gl.uniform3fv(U('Ldir'),o.Ldir||[-.55,.62,-.45]);gl.uniform3fv(U('Lcol'),o.Lcol||[1.08,.92,.74]);gl.uniform3fv(U('Acol'),o.Acol||[.5,.6,.8]);
    for(const [k,v] of Object.entries({span:1.25,layer:0,zSplit:18,wheelA:0,T:0,sunset:0,fogK:.014,fogStart:12,groundY:0,useGround:1,tmaxU:160}))gl.uniform1f(U(k),o[k]??v);
    gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);gl.drawArrays(gl.TRIANGLES,0,3);gl.finish();return 1};
}
