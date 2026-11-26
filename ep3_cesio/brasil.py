import numpy as np,base64,io
from PIL import Image,ImageDraw
from scipy import ndimage
src=open('/home/claude/holanda/geo.js').read()+open('/home/claude/holanda/papi_scenes.js').read()
def get(name):
  a=src.index('const '+name+'=')+len('const '+name+'=')
  if name=='REST':
    b=src.index(',...[...BR]',a);return eval(src[a:b]+']')+list(reversed(get('BR')))[1:]
  b=src.index(';',a);return eval(src[a:b])
REST,BR=get('REST'),get('BR')
LON0,LON1,LAT0,LAT1=-76.,-30.,-36.,10.
TW=TH=2048
def px(la,lo):return ((lo-LON0)/(LON1-LON0)*TW,(LAT1-la)/(LAT1-LAT0)*TH)
im=Image.new('L',(TW,TH),0);d=ImageDraw.Draw(im)
for P in [REST,BR]:d.polygon([px(*q) for q in P],fill=255)
m=np.array(im)>127
rng=np.random.default_rng(5)
n=ndimage.gaussian_filter(rng.normal(size=(TH//8,TW//8)),2);n=np.kron(n,np.ones((8,8)))[:TH,:TW]
f=ndimage.gaussian_filter(m.astype(float),3)+n*.2;m=f>.5
din=ndimage.distance_transform_edt(m);dout=ndimage.distance_transform_edt(~m)
hn=ndimage.gaussian_filter(rng.normal(size=(TH//4,TW//4)),3);hn=np.kron(hn,np.ones((4,4)))[:TH,:TW];hn=(hn-hn.min())/(hn.max()-hn.min())
H=np.where(m,np.clip(din/90,0,1)**.6*(.55+.45*hn),0);D=np.clip(dout/260,0,1)
img=np.stack([H*255,D*255,m*255],-1).astype('uint8')
b=io.BytesIO();Image.fromarray(img).save(b,'PNG')
s=open('map3d_src.html').read().replace('__B64__',base64.b64encode(b.getvalue()).decode())
open('brasil3d.html','w').write(s)
# Brasil (contorno) em coordenadas do mundo, para desenhar a fronteira por cima
geo=lambda la,lo:((lo-(LON0+LON1)/2)/((LON1-LON0)/2)*1.6,((la-(LAT0+LAT1)/2)/((LAT1-LAT0)/2))*1.6)
import json;json.dump(dict(BR=[geo(*q) for q in BR],goiania=geo(-16.68,-49.25)),open('brasil_geo.json','w'))
print('ok',m.mean(),geo(-16.68,-49.25))
