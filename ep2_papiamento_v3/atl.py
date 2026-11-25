import re,numpy as np,base64,io
from PIL import Image,ImageDraw
from scipy import ndimage
src=open('geo.js').read()+open('papi_scenes.js').read()
def get(name):
  a=src.index('const '+name+'=')+len('const '+name+'=')
  if name=='REST':
    b=src.index(',...[...BR]',a);return eval(src[a:b]+']')+list(reversed(get('BR')))[1:]
  b=src.index(';',a);return eval(src[a:b])
REST,AFR,IBR,BR=get('REST'),get('AFR'),get('IBR'),get('BR')
CAM=[[8.5,-77.4],[9.4,-79.9],[8.2,-82.9],[9.9,-85.7],[11.0,-85.9],[12.6,-87.6],[13.4,-89.8],[14.5,-92.3],[16.0,-94.5],[15.8,-96.6],[17.0,-100.5],[18.4,-103.5],[20.0,-105.5],[23.0,-106.4],[26,-111],[32,-117],[45,-125],[45,-60],[47,-60],[45,-66],[41,-70],[40,-74],[37,-76],[35,-76],[32,-81],[30.7,-81.4],[29.5,-81.2],[27,-80],[25.4,-80.3],[25.2,-81],[27,-82.3],[29,-83],[30,-84],[30.4,-87],[29,-93],[27.8,-97.2],[25.9,-97.2],[23,-97.8],[21.2,-97.3],[19.2,-96.1],[18.5,-94.5],[18.6,-91.5],[19.8,-90.5],[21.2,-90.0],[21.5,-87.0],[18.5,-87.8],[16.0,-88.6],[15.8,-87],[15.9,-84],[15.0,-83.2],[12.0,-83.6],[10.9,-83.6],[9.6,-82.4],[9.3,-79.6],[8.6,-77.8]]
CUBA=[[22.0,-84.9],[22.9,-83.0],[23.2,-80.5],[22.2,-77.5],[21.2,-75.6],[20.1,-74.2],[19.9,-75.6],[20.0,-77.7],[21.0,-78.5],[21.7,-81.9],[21.8,-83.9]]
HISP=[[19.9,-72.8],[19.7,-70.0],[19.2,-68.5],[18.3,-68.4],[18.2,-70.2],[18.0,-71.5],[18.3,-74.4],[18.6,-74.3],[19.3,-72.8]]
PR=[[18.5,-67.2],[18.4,-65.6],[18.0,-65.8],[18.0,-67.2]];JAM=[[18.5,-78.3],[18.4,-76.3],[17.9,-76.2],[17.9,-77.7]]
TRI=[[10.8,-61.5],[10.7,-60.9],[10.1,-61.0],[10.1,-61.9]]
EUR=[[43.4,-8.3],[43.5,-1.5],[46.5,-1.2],[48.5,-4.7],[50,-5],[51,1.5],[53,4.5],[54,8.5],[58,8],[62,5],[62,25],[46,25],[43.4,3]]
LON0,LON1,LAT0,LAT1=-92.,18.,-28.,32.
TW=2048;TH=int(2048*(LAT1-LAT0)/(LON1-LON0))
def px(la,lo):return ((lo-LON0)/(LON1-LON0)*TW,(LAT1-la)/(LAT1-LAT0)*TH)
im=Image.new('L',(TW,TH),0);d=ImageDraw.Draw(im)
for P in [REST,BR,AFR,IBR,CAM,CUBA,HISP,PR,JAM,TRI,EUR]:d.polygon([px(*q) for q in P],fill=255)
for la,lo in [(12.5,-69.97),(12.2,-68.95),(12.17,-68.28)]:
  x,y=px(la,lo);d.ellipse([x-3,y-3,x+3,y+3],fill=255)
m=np.array(im)>127
rng=np.random.default_rng(5)
n=ndimage.gaussian_filter(rng.normal(size=(TH//8+1,TW//8+1)),2);n=np.kron(n,np.ones((8,8)))[:TH,:TW]
f=ndimage.gaussian_filter(m.astype(float),2)+n*.25;m=f>.5
din=ndimage.distance_transform_edt(m);dout=ndimage.distance_transform_edt(~m)
hn=ndimage.gaussian_filter(rng.normal(size=(TH//4+1,TW//4+1)),3);hn=np.kron(hn,np.ones((4,4)))[:TH,:TW];hn=(hn-hn.min())/(hn.max()-hn.min())
H=np.where(m,np.clip(din/40,0,1)**.6*(.45+.55*hn),0);D=np.clip(dout/120,0,1)
img=np.stack([H*255,D*255,m*255],-1).astype('uint8')
b=io.BytesIO();Image.fromarray(img).save(b,'PNG');open('atl_tex.b64','w').write(base64.b64encode(b.getvalue()).decode())
Image.fromarray(img).save('atl_tex.png');print(TW,TH)
