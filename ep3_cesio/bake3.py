"""Placas de cenário do episódio 3 (césio-137) + posições projetadas para textos/efeitos. uso: bake3.py [nomes...]"""
import os, sys, json, math, time
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/opt/pw-browsers'
import numpy as np
from playwright.sync_api import sync_playwright
from PIL import Image, ImageFilter
D = '/home/claude/cesio'; A = f'{D}/ep3'; os.makedirs(A, exist_ok=True)
H = 1920; M = 110; PW = 1080 + 2 * M
MAN = json.load(open(f'{A}/manifest.json')) if os.path.exists(f'{A}/manifest.json') else {}
def save(): json.dump(MAN, open(f'{A}/manifest.json', 'w'), indent=1, ensure_ascii=False)
def nrm(v): v = np.array(v, float); return v / np.linalg.norm(v)
class Cam:
    def __init__(s, camP, camT, span, W=PW):
        s.ro = np.array(camP, float); s.ta = np.array(camT, float); s.span = span; s.W = W
        s.ww = nrm(s.ta - s.ro); s.uu = nrm(np.cross([0, 1, 0], s.ww)); s.vv = np.cross(s.ww, s.uu)
    def proj(s, P):
        d = np.array(P, float) - s.ro; x, y, z = d @ s.uu, d @ s.vv, d @ s.ww
        return [round(s.W / 2 + x / z * s.span * H, 1), round(H / 2 - y / z * s.span * H, 1), round(float(z), 3)]
    def args(s): return dict(camP=list(s.ro), camT=list(s.ta), span=s.span)
PG = {}
def page(pw, name):
    if name not in PG:
        b = pw.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = b.new_page(); pg.on('pageerror', lambda e: print('ERR', str(e)[:800])); pg.goto(f'file://{D}/{name}'); PG[name] = pg
    return PG[name]
def render(pw, name, o, out):
    if os.environ.get('SKIP') and os.path.exists(out): return
    pg = page(pw, name); t = time.time(); pg.set_viewport_size({"width": o["w"], "height": o["h"]})
    pg.evaluate("o=>draw(o)", o); pg.locator('#c').screenshot(path=out, omit_background=True); print(os.path.basename(out), round(time.time() - t, 1), flush=True)
DAY = dict(Ldir=[-.55, .62, -.45], Lcol=[1.08, .92, .74], Acol=[.5, .6, .8])
IN = dict(useGround=0, fogK=0., fogStart=50, tmaxU=40, Ldir=[-.5, .7, -.5], Lcol=[1.0, .9, .75], Acol=[.85, .78, .68])
DUSK = dict(sunset=1, Ldir=[-.8, .25, -.3], Lcol=[1.0, .62, .5], Acol=[.45, .5, .8])
STU = dict(useGround=0, fogK=0., tmaxU=30, Ldir=[-.6, .8, -.3], Lcol=[.95, .82, .66], Acol=[.45, .5, .62])
# nome: (arquivo, câmera, luz, camadas[(layer, nome, blur)], pontos 3D a projetar)
CAMS = {
 'hook':  ('estudio.html', ([0.75, .9, -3.0], [0.1, .3, 0], 1.45), STU, [(3, 'back', 14), (0, 'near', 0), (6, 'glow', 0)], dict(po=[.55, .12, -.25], boca=[-.1, .3, -.05])),
 'fim':   ('estudio.html', ([-.5, .8, -2.6], [.3, .25, 0], 1.5), STU, [(3, 'back', 14), (0, 'near', 0), (6, 'glow', 0)], dict(po=[.55, .12, -.25], boca=[-.1, .3, -.05])),
 'tonel': ('deposito.html', ([0.5, 1.5, -4.5], [0.6, 1.0, 10], 1.15), DAY, [(1, 'bg', 0), (2, 'fg', 10)], {}),
 'aterro':('deposito.html', ([1, 4.2, -8], [2, 1.5, 14], 1.05), DAY, [(1, 'bg', 0)], dict(morro=[2, 2.4, 15], placa=[-3.2, 2.62, 3.94])),
 'clin':  ('rua.html', ([-4, 1.7, -11], [-4, 2.6, 10], 1.05), DAY, [(1, 'bg', 0), (2, 'fg', 14)], dict(maq=[-6.4, 2.9, 4.4])),
 'clin2': ('rua.html', ([-2.5, 1.5, -8.5], [-2.5, 1.9, 10], 1.1), DAY, [(1, 'bg', 0)], {}),
 'onibus':('rua.html', ([0, 1.6, -18], [0, 1.8, 10], 1.05), DAY, [(1, 'bg', 0), (5, 'bus', 0)], {}),
 'vig':   ('rua.html', ([12.5, 1.6, -9], [12.8, 2.0, 10], 1.1), DAY, [(1, 'bg', 0)], dict(placa=[[10.6, 3.37, 1.79], [15.4, 3.37, 1.79], [15.4, 2.53, 1.79], [10.6, 2.53, 1.79]])),
 'ferro': ('ferro.html', ([-0.6, 2.2, -7.5], [1.0, 1.6, 6], 1.1), DAY, [(1, 'bg', 0)], dict(placa=[[0.15, 4.24, 1.39], [3.85, 4.24, 1.39], [3.85, 3.46, 1.39], [0.15, 3.46, 1.39]])),
 'noite': ('ferro.html', ([1.8, 1.5, -3.5], [2.0, 1.2, 10], 1.2), DUSK, [(1, 'bg', 0), (0, 'mesa', 0), (6, 'glow', 0)], dict(peca=[1.8, 1.02, 3.2], lamp=[1.8, 2.3, 3.4])),
 'noite2':('ferro.html', ([1.6, 1.8, -5.2], [1.9, 1.1, 10], 1.1), DUSK, [(1, 'bg', 0), (0, 'mesa', 0), (6, 'glow', 0)], dict(peca=[1.8, 1.02, 3.2], lamp=[1.8, 2.3, 3.4])),
 'coz1':  ('interior.html', ([0.15, 1.45, -2.4], [0, 1.0, 6], 1.15), dict(IN, sunset=0), [(1, 'room', 0), (0, 'mesa', 0), (6, 'glow', 0)], dict(po=[0, .8, .95], lamp=[0, 2.15, 1.1])),
 'coz2':  ('interior.html', ([0.3, 1.6, -3.6], [0.1, 1.15, 6], 1.0), dict(IN, sunset=0), [(1, 'room', 0), (0, 'mesa', 0), (6, 'glow', 0)], dict(po=[0, .8, .95], lamp=[0, 2.15, 1.1])),
 'escr':  ('interior.html', ([0.4, 1.55, -2.6], [0.2, 1.15, 6], 1.15), dict(IN, sunset=1), [(1, 'room', 0), (0, 'mesa', 0)], dict(bolsa=[.55, .95, .85])),
 'lab':   ('interior.html', ([0.1, 1.5, -2.2], [0, 1.1, 6], 1.2), dict(IN, sunset=2), [(1, 'room', 0), (0, 'mesa', 0)], dict(pote=[-.1, 1.3, .8])),
 'estadio':('estadio.html', ([0, 1.9, -8], [0, 2.2, 10], 1.05), DAY, [(1, 'bg', 0), (2, 'fg', 12)], {}),
 'memo':  ('cemiterio.html', ([0, 0.95, -2.7], [0, .95, 4], 1.15), DAY, [(1, 'bg', 0), (6, 'chama', 0)], dict(lapide=[[-.7, 1.38, .26], [.7, 1.38, .26], [.7, .62, .26], [-.7, .62, .26]], v1=[-.25, .66, -.6], v2=[.25, .66, -.6])),
 'enterro':('cemiterio.html', ([4.5, 1.7, -6], [5, 0.9, 10], 1.1), DAY, [(1, 'bg', 0), (2, 'fg', 12)], dict(c1=[4.4, .6, 2.4], c2=[5.6, .6, 2.4])),
}
def bake(pw, names):
    for nm in names:
        f, (cp, ct, sp), lt, lays, pts = CAMS[nm]; cam = Cam(cp, ct, sp)
        base = dict(cam.args(), w=PW, h=H, **lt); L = {}
        for lay, ln, bl in lays:
            fn = f'{nm}_{ln}.png'; render(pw, f, dict(base, layer=lay), f'{A}/{fn}')
            if bl: Image.open(f'{A}/{fn}').filter(ImageFilter.GaussianBlur(bl)).save(f'{A}/{fn}')
            if ln in ('bg', 'room'): Image.open(f'{A}/{fn}').convert('RGB').save(f'{A}/{nm}_{ln}.jpg', quality=92); fn = f'{nm}_{ln}.jpg'
            L[ln] = fn
        P = {k: ([cam.proj(q) for q in v] if isinstance(v[0], list) else cam.proj(v)) for k, v in pts.items()}
        MAN[nm] = dict(layers=L, pts=P, cam=dict(camP=cp, camT=ct, span=sp)); save()
def bake_map(pw):
    g = json.load(open(f'{D}/brasil_geo.json')); gx, gz = g['goiania']
    cam = Cam([0.12, 4.9, -2.0], [0.12, 0, 0.0], 1.0)
    o = dict(cam.args(), w=PW, h=H, T=1., pin0=[gx, .05, gz], pinH0=2.2)
    render(pw, 'brasil3d.html', o, f'{A}/mapa.png'); Image.open(f'{A}/mapa.png').convert('RGB').save(f'{A}/mapa.jpg', quality=93)
    MAN['mapa'] = dict(src='mapa.jpg', br=[cam.proj([x, .045, z])[:2] for x, z in g['BR']], pin=cam.proj([gx, .05 + .38, gz])); save()
if __name__ == '__main__':
    names = sys.argv[1:] or list(CAMS) + ['mapa']
    with sync_playwright() as pw:
        bake(pw, [n for n in names if n in CAMS])
        if 'mapa' in names: bake_map(pw)
