import numpy as np,base64,io,json
from PIL import Image,ImageDraw
from scipy import ndimage
LON0,LON1,LAT0,LAT1=-71.0,-67.8,10.4,13.6
TW,TH=2048,2048
MAIN=[[11.0,-73.5],[11.3,-73.5],[11.8,-72.6],[12.2,-72.2],[12.45,-71.7],[12.2,-71.2],[11.85,-71.35],[11.4,-71.55],[10.95,-71.6],[11.2,-70.9],[11.45,-70.25],[11.62,-70.2],[11.75,-70.3],[12.0,-70.3],[12.2,-70.0],[11.95,-69.8],[11.7,-69.9],[11.55,-69.75],[11.5,-69.6],[11.45,-69.2],[11.4,-68.6],[11.1,-68.45],[10.85,-68.3],[10.5,-68.0],[10.6,-67.0],[10.5,-66.0],[9.5,-66.0],[9.5,-73.5]]
ARU=[[12.625,-70.06],[12.59,-70.02],[12.53,-69.96],[12.47,-69.90],[12.43,-69.87],[12.41,-69.88],[12.44,-69.93],[12.50,-70.0],[12.55,-70.05],[12.60,-70.07]]
CUR=[[12.39,-69.16],[12.37,-69.11],[12.30,-69.04],[12.22,-68.95],[12.16,-68.86],[12.10,-68.80],[12.05,-68.74],[12.03,-68.75],[12.06,-68.83],[12.10,-68.90],[12.16,-68.98],[12.22,-69.06],[12.28,-69.12],[12.33,-69.16]]
BON=[[12.30,-68.39],[12.28,-68.31],[12.23,-68.25],[12.18,-68.20],[12.12,-68.21],[12.08,-68.25],[12.03,-68.27],[12.05,-68.30],[12.12,-68.29],[12.17,-68.30],[12.22,-68.34],[12.26,-68.41]]
def px(la,lo):return ((lo-LON0)/(LON1-LON0)*TW,(LAT1-la)/(LAT1-LAT0)*TH)
im=Image.new('L',(TW,TH),0);d=ImageDraw.Draw(im)
for P in [MAIN,ARU,CUR,BON]:d.polygon([px(*q) for q in P],fill=255)
x,y=px(12.16,-68.32);d.ellipse([x-12,y-12,x+12,y+12],fill=255)
m=np.array(im)>127
# contornos menos poligonais: desfoca e re-limiar + ruído de borda
rng=np.random.default_rng(3)
n=ndimage.gaussian_filter(rng.normal(size=(TH//8,TW//8)),2);n=np.kron(n,np.ones((8,8)))[:TH,:TW]
f=ndimage.gaussian_filter(m.astype(float),4)+n*.25
m=f>.5
din=ndimage.distance_transform_edt(m);dout=ndimage.distance_transform_edt(~m)
hn=ndimage.gaussian_filter(rng.normal(size=(TH//4,TW//4)),3);hn=np.kron(hn,np.ones((4,4)))[:TH,:TW];hn=(hn-hn.min())/(hn.max()-hn.min())
H=np.where(m,np.clip(din/60,0,1)**.6*(.55+.45*hn),0)
D=np.clip(dout/220,0,1)
img=np.stack([H*255,D*255,m*255],-1).astype('uint8')
Image.fromarray(img).save('map_tex.png')
b=io.BytesIO();Image.fromarray(img).save(b,'PNG');open('map_tex.b64','w').write(base64.b64encode(b.getvalue()).decode())
print('ok',m.mean())
