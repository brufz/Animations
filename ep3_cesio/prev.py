"""Pré-visualiza um cenário: prev.py arquivo.html saida.png 'camP' 'camT' span [extra json]"""
import os,sys,json
os.environ['PLAYWRIGHT_BROWSERS_PATH']='/opt/pw-browsers'
from playwright.sync_api import sync_playwright
from PIL import Image
f,out,cp,ct,sp=sys.argv[1:6];ex=json.loads(sys.argv[6]) if len(sys.argv)>6 else {}
W,H=int(ex.pop('W',540)),int(ex.pop('H',960));lays=ex.pop('layers',[1,2])
with sync_playwright() as p:
  b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"]);pg=b.new_page(viewport={"width":W,"height":H});pg.on('pageerror',lambda e:print('ERR',str(e)[:1500]))
  pg.goto(f'file:///home/claude/cesio/{f}')
  ims=[]
  for L in lays:
    pg.evaluate("o=>draw(o)",dict(camP=json.loads(cp),camT=json.loads(ct),span=float(sp),w=W,h=H,layer=L,**ex));pg.locator('#c').screenshot(path=f'/tmp/_l{L}.png',omit_background=True);ims.append(Image.open(f'/tmp/_l{L}.png').convert('RGBA'))
  b.close()
c=ims[0]
for i in ims[1:]:c.alpha_composite(i)
c.convert('RGB').save(out)
