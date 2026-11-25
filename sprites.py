import os,sys,json,math,time;os.environ['PLAYWRIGHT_BROWSERS_PATH']='/opt/pw-browsers'
from playwright.sync_api import sync_playwright
from PIL import Image
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'sprites');os.makedirs(D,exist_ok=True)
H=lambda s:[int(s[i:i+2],16)/255 for i in (1,3,5)]
skins=['#f1c9a5','#d9a27a','#a8704a','#6e4428']
VAR=[ # camisa, calça, pele, cabelo, chapéu, hatT, saia
 ('#c8553d','#3b2a22',0,'#3a2414','#2a2420',1,0),('#2f7f7a','#4a3a2a',2,'#1d1712','#2a2420',0,0),('#e3a33b','#5a4636',1,'#5b3a22','#2a2420',0,1),
 ('#3e6e8f','#3b2a22',3,'#120c08','#efe7d6',2,1),('#f1e3c3','#5a4636',1,'#2a1a10','#6b4a2a',1,0),('#8c3b3b','#2f3a4a',0,'#8a5a2a','#c8553d',2,1),
 ('#5f9a52','#3b2a22',3,'#120c08','#2a2420',1,0),('#d9824a','#2f3a4a',2,'#1d1712','#2a2420',0,0),('#a34a3a','#4a3a2a',1,'#3a2414','#f1e3c3',2,1),('#e8c26a','#3b2a22',0,'#c99a55','#2a2420',0,0)]
def shot(pg,o,path):
  pg.set_viewport_size({"width":o['w'],"height":o['h']})
  pg.evaluate("o=>draw(o)",o)
  pg.locator('#c').screenshot(path=path,omit_background=True)
def strip(paths,out):
  ims=[Image.open(p) for p in paths];w,h=ims[0].size
  s=Image.new('RGBA',(w*len(ims),h));[s.paste(im,(i*w,0)) for i,im in enumerate(ims)];s.save(out)
  [os.remove(p) for p in paths]
with sync_playwright() as p:
  b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"]);pg=b.new_page(viewport={"width":300,"height":500})
  pg.on('pageerror',lambda e:print('ERR',str(e)[:800]))
  pg.goto('file://'+os.path.join(os.path.dirname(os.path.abspath(__file__)),'chars3d.html'));t0=time.time()
  only=sys.argv[1:]
  base=dict(w=240,h=400,span=1.5,cy=.66,cx=0)
  if not only or 'people' in only:
    for i,(sh_,pa,sk,ha,hat,ht,sk2) in enumerate(VAR):
      fr=[]
      for f in range(6):
        pose=.5-.5*math.cos(f/6*2*math.pi)
        o=dict(base,K=1,cShirt=H(sh_),cPants=H(pa),cSkin=H(skins[sk]),cHair=H(ha),cHat=H(hat),hatT=ht,skirt=sk2,pose=pose,smile=1 if pose>.3 else 0,yaw=(-.25 if i%2 else .25))
        fp=f'{D}/_p{i}_{f}.png';shot(pg,o,fp);fr.append(fp)
      strip(fr,f'{D}/pv{i}.png')
    print('people',time.time()-t0,flush=True)
  if not only or 'soldier' in only:
    for i,(coat,sk) in enumerate([('#26324f',0),('#2b3a5c',1),('#33415f',0)]):
      o=dict(base,h=520,span=2.0,cy=.95,K=2,cShirt=H(coat),cPants=H('#5a5a62'),cSkin=H(skins[sk]),cHair=H('#3a2414'),cHat=H('#1d1d22'),hatT=1,pose=0,yaw=.3)
      shot(pg,o,f'{D}/sold{i}.png')
  if not only or 'painter' in only:
    fr=[]
    for f in range(6):
      o=dict(base,K=3,cShirt=H('#6b3b2a'),cPants=H('#3a2a22'),cSkin=H(skins[0]),cHair=H('#8a5a2a'),cHat=H('#2a2420'),hatT=0,yaw=-.5+.05*math.sin(f),T=f)
      fp=f'{D}/_pa{f}.png';shot(pg,o,fp);fr.append(fp)
    strip(fr,f'{D}/painter.png')
  if not only or 'player' in only:
    fr=[]
    for f in range(8):
      pose=.75+.25*math.sin(f/8*2*math.pi)
      o=dict(base,w=300,h=500,K=4,cShirt=H('#f08a24'),cPants=H('#1d1d22'),cSkin=H(skins[2]),cHair=H('#120c08'),cHat=H('#000000'),hatT=0,pose=pose,smile=1,yaw=0)
      fp=f'{D}/_pl{f}.png';shot(pg,o,fp);fr.append(fp)
    strip(fr,f'{D}/player.png')
  if not only or 'nassau' in only:
    fr=[]
    for f in range(8):
      o=dict(w=320,h=560,span=3.0,cy=1.35,cx=0,K=0,T=f/8*2*math.pi/6,wave=1,yaw=.15)
      fp=f'{D}/_n{f}.png';shot(pg,o,fp);fr.append(fp)
    strip(fr,f'{D}/nassau.png')
  if not only or 'ox' in only:
    fr=[]
    for f in range(4):
      o=dict(w=560,h=420,span=1.9,cy=.75,cx=.15,K=5,T=f/4*2*math.pi/4,yaw=.35)
      fp=f'{D}/_o{f}.png';shot(pg,o,fp);fr.append(fp)
    strip(fr,f'{D}/ox.png')
  print('total',time.time()-t0)
  b.close()
