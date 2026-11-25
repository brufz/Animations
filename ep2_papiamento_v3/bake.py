"""Gera todos os assets 3D do episódio 2 (papiamento v3): placas de cenário em camadas,
sprites dos personagens e o manifesto JSON usado pela página ep2.html.
uso: python3 bake.py [park|water|class|maps|chars|all]"""
import os, sys, json, math, time
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/opt/pw-browsers'
import numpy as np
from playwright.sync_api import sync_playwright
from PIL import Image, ImageFilter
D = '/home/claude/holanda'; A = f'{D}/ep2'; os.makedirs(A, exist_ok=True)
H = 1920; M = 110; PW = 1080 + 2 * M
MAN = json.load(open(f'{A}/manifest.json')) if os.path.exists(f'{A}/manifest.json') else {}
def save(): json.dump(MAN, open(f'{A}/manifest.json', 'w'), indent=1, ensure_ascii=False)
def nrm(v): v = np.array(v, float); return v / np.linalg.norm(v)
class Cam:
    def __init__(s, camP, camT, span, W=PW, pb=False):
        s.ro = np.array(camP, float); s.ta = np.array(camT, float); s.span = span; s.W = W; s.pb = pb
        s.ww = nrm(s.ta - s.ro); s.uu = nrm(np.cross([0, 1, 0], s.ww)); s.vv = np.cross(s.ww, s.uu)
        s.kk = np.linalg.norm(s.ta - s.ro) / span
    def proj(s, P):
        d = np.array(P, float) - s.ro
        if s.pb:
            x = d @ s.uu / s.kk; d2 = d - s.uu * (d @ s.uu); y = d2 @ s.vv / (d2 @ s.ww) * s.span
            return s.W / 2 + x * H, H / 2 - y * H, d2 @ s.ww
        x, y, z = d @ s.uu, d @ s.vv, d @ s.ww
        return s.W / 2 + x / z * s.span * H, H / 2 - y / z * s.span * H, z
    def ppu(s, P): return s.span * H / s.proj(P)[2]
    def args(s): return dict(camP=list(s.ro), camT=list(s.ta), span=s.span)
PG = {}
def page(pw, name):
    if name not in PG:
        b = pw.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = b.new_page(); pg.on('pageerror', lambda e: print('ERR', str(e)[:800]))
        pg.goto(f'file://{D}/{name}')
        if 'map' in name or 'atl' in name: pg.evaluate("()=>ready")
        PG[name] = pg
    return PG[name]
def render(pw, name, o, out, ss=1):
    if os.environ.get('SKIP') and os.path.exists(out) and 'chars' not in name: return
    pg = page(pw, name); t = time.time()
    w, h = o['w'], o['h']; o = dict(o, w=int(w * ss), h=int(h * ss))
    pg.set_viewport_size({"width": o["w"], "height": o["h"]})
    pg.evaluate("o=>draw(o)", o); pg.locator('#c').screenshot(path=out, omit_background=True)
    if ss != 1: Image.open(out).resize((w, h), Image.LANCZOS).save(out)
    print(os.path.basename(out), round(time.time() - t, 1), flush=True)
def blur(src, out, r):
    Image.open(src).filter(ImageFilter.GaussianBlur(r)).save(out)
# ---------------------------------------------------------------- personagens
CH = {
 'mae':   dict(hair=2, outfit=2, cShirt="#f08a3c", cSkin="#7a4a30", cHair="#1a1210"),
 'filha': dict(kid=1, hair=3, outfit=0, cShirt="#4aa3df", cPants="#f6d55c", cSkin="#e8b48f", cHair="#5a3a22"),
 'guia':  dict(hat=1, outfit=1, cShirt="#1f8a70", cHat="#f2c14e", cAcc="#c0392b"),
 'local': dict(hat=3, outfit=2, cShirt="#f6c445", cHat="#c0392b", cSkin="#5e3a24", cHair="#120c08"),
 'senhor': dict(hat=2, outfit=3, beard=1, cShirt="#f4efe2", cAcc="#2f7f7a", cHat="#e3c27a", cPants="#6b4a32", cSkin="#8a5a3a", cHair="#2a1a10"),
 'moca':  dict(hair=1, outfit=2, cShirt="#7cc3e8", cSkin="#6e4428", cHair="#1d1712"),
 'rapaz': dict(hair=0, outfit=0, cShirt="#f6c445", cPants="#2f3a55", cSkin="#4e3020", cHair="#120c08"),
 'menino': dict(kid=1, hair=2, outfit=0, cShirt="#e8483a", cPants="#2f3a55", cSkin="#5e3a24", cHair="#120c08"),
 'prof':  dict(hair=3, outfit=2, glasses=1, cShirt="#3b3346", cSkin="#e0b090", cHair="#4a3020"),
 'aluno1': dict(kid=1, hair=0, outfit=3, cShirt="#f4efe2", cAcc="#3e6e8f", cPants="#4a3a2a", cSkin="#6e4428", cHair="#120c08"),
 'aluno2': dict(kid=1, hair=1, outfit=2, cShirt="#f4efe2", cSkin="#8a5a3a", cHair="#1d1712"),
 'aluno3': dict(kid=1, hair=2, outfit=3, cShirt="#f4efe2", cAcc="#8c3b3b", cPants="#4a3a2a", cSkin="#5e3a24", cHair="#120c08"),
}
def sprite(pw, scn, cam, nm, who, P, face, base={}, states=None):
    """renderiza o personagem 'who' na posição P (mundo) vista pela câmera; states: dict nome->params extras"""
    ppu = cam.ppu(P); x, y, z = cam.proj(P)
    h = int(math.ceil(2.25 * ppu / 2) * 2); w = int(math.ceil(1.9 * ppu / 2) * 2)
    cy = 1.0; span_c = h / ppu
    pitch = (cam.ro[1] - 0.95) / max(.5, (np.array(P) - cam.ro) @ cam.ww)
    yw = face + math.atan2(P[0] - cam.ro[0], P[2] - cam.ro[2])
    footY = h / 2 + cy * ppu
    states = states or {'base': {}}
    fr = {}
    for k, extra in states.items():
        o = {**CH[who], **base, **extra, 'w': w, 'h': h, 'span': span_c, 'cy': cy, 'pitchC': pitch, 'yaw': yw}
        if 'yawAdd' in o: o['yaw'] += o.pop('yawAdd')
        fn = f'{scn}_{nm}_{k}.png'; render(pw, 'chars_v2.html', o, f'{A}/{fn}'); fr[k] = fn
    return dict(frames=fr, x=round(x - w / 2), y=round(y - footY), w=w, h=h, z=float(z), par=round(min(2.2, 7.5 / z), 3))
def wave_states(prefix='w', n=6, talk=False, side='R', base_open=0):
    st = {}
    for i in range(n):
        a = math.sin(i / n * 2 * math.pi)
        arm = {f'a{side}': .84 + .1 * a, f'b{side}': .42 + .28 * a}
        st[f'{prefix}{i}'] = dict(arm, smile=base_open)
        if talk: st[f'{prefix}{i}o'] = dict(arm, smile=1)
    return st
def talk_states(): return {'base': dict(smile=0), 'open': dict(smile=1), 'blink': dict(smile=0, blink=1)}
def happy_states(): return {'base': dict(smile=1), 'blink': dict(smile=1, blink=1)}
# ---------------------------------------------------------------- cenas
def bake_park(pw):
    camA = Cam([0.3, 1.05, -8], [0.3, 1.45, 10], 1.25)
    camB = Cam([-1.7, 1.25, -7.2], [1.3, 1.4, 10], 1.25)
    out = {}
    for tag, cam, sun in [('A', camA, 0), ('B', camB, 0), ('S', camA, 1)]:
        lt = dict(Ldir=[-.55, .62, -.45], Lcol=[1.08, .92, .74], Acol=[.5, .6, .8]) if not sun else dict(Ldir=[-.8, .32, -.35], Lcol=[1.25, .78, .5], Acol=[.45, .42, .62], sunset=1)
        base = dict(cam.args(), w=PW, h=H, **lt)
        L = {}
        for lay, nm, par in [(1, 'sky', .15), (4, 'far', .35), (0, 'near', .75), (2, 'fg', 1.9)]:
            fn = f'park{tag}_{nm}.png'; render(pw, 'park3.html', dict(base, layer=lay), f'{A}/{fn}')
            if nm == 'fg': blur(f'{A}/{fn}', f'{A}/{fn}', 16)
            L[nm] = dict(src=fn, par=par)
        wf = []
        for i in range(16):
            fn = f'park{tag}_wheel{i:02d}.png'; render(pw, 'park3.html', dict(base, layer=3, wheelA=i / 16 * (2 * math.pi / 12)), f'{A}/{fn}'); wf.append(fn)
        L['wheel'] = dict(frames=wf, par=.22)
        out[tag] = L
    S = {}
    S['A'] = dict(mae=sprite(pw, 'pkA', camA, 'mae', 'mae', [-0.72, 0, -0.6], -.5, dict(lookX=1), happy_states()),
                  filha=sprite(pw, 'pkA', camA, 'filha', 'filha', [-0.12, 0, -1.75], -.65, dict(lookX=1, lookY=.3), happy_states()),
                  guia=sprite(pw, 'pkA', camA, 'guia', 'guia', [1.05, 0, -1.3], .6, dict(lookX=-1, smile=1), wave_states()))
    S['B'] = dict(mae=sprite(pw, 'pkB', camB, 'mae', 'mae', [-1.55, 0, -4.6], math.pi - .35, {}, {'base': {}}),
                  filha=sprite(pw, 'pkB', camB, 'filha', 'filha', [-1.3, 0, -2.7], math.pi - .7, {}, {'base': dict(aR=.9, bR=.3)}),
                  guia=sprite(pw, 'pkB', camB, 'guia', 'guia', [-0.4, 0, -1.6], -.25, dict(lookX=-.6), wave_states(talk=True)))
    S['S'] = dict(mae=sprite(pw, 'pkS', camA, 'mae', 'mae', [-0.72, 0, -0.6], -.3, dict(lookX=.3, smile=1), wave_states('w', 6, False, 'L', 1)),
                  filha=sprite(pw, 'pkS', camA, 'filha', 'filha', [-0.12, 0, -1.75], -.2, dict(smile=1), wave_states('w', 6, False, 'R', 1)),
                  guia=sprite(pw, 'pkS', camA, 'guia', 'guia', [1.05, 0, -1.3], .35, dict(lookX=-.4, smile=1), wave_states()))
    MAN['park'] = dict(layers=out, sprites=S); save()
def bake_water(pw):
    lt = dict(useGround=0, Ldir=[-.45, .75, -.5], Lcol=[1.15, 1., .85], Acol=[.5, .62, .85], fogK=.008, fogStart=20)
    cams = {'A': Cam([0., 1.75, -8], [0., 1.45, 10], 1.25), 'B': Cam([3.4, 1.7, -7.8], [2.6, 1.45, 10], 1.25)}
    out = {}
    for tag, cam in cams.items():
        base = dict(cam.args(), w=PW, h=H, **lt); L = {}
        for lay, nm, par in [(1, 'far', .25), (0, 'near', .75), (2, 'fg', 1.9)]:
            fn = f'cais{tag}_{nm}.png'; render(pw, 'waterfront.html', dict(base, layer=lay, T=1.), f'{A}/{fn}')
            if nm == 'far':
                im = Image.open(f'{A}/{fn}'); y0 = int(cam.proj([cam.ro[0], -.6, 15])[1]) - 4; y1 = int(cam.proj([cam.ro[0], -.6, 2.2])[1]) + 6
                band = im.crop((0, y0, im.width, y1)).filter(ImageFilter.BoxBlur(2)); im.paste(band, (0, y0)); im.save(f'{A}/{fn}')
            if nm == 'fg': blur(f'{A}/{fn}', f'{A}/{fn}', 16)
            L[nm] = dict(src=fn, par=par)
        out[tag] = L
    cA, cB = cams['A'], cams['B']
    S = {}
    S['A'] = dict(local=sprite(pw, 'caA', cA, 'local', 'local', [-0.6, 0, -1.3], -.55, dict(lookX=1, aR=.55, bR=.6, fwdR=.4), talk_states()),
                  filha=sprite(pw, 'caA', cA, 'filha', 'filha', [0.75, 0, -1.9], .6, dict(lookX=-1, lookY=.4), happy_states()),
                  senhor=sprite(pw, 'caA', cA, 'senhor', 'senhor', [-1.55, 0, 0.6], -.3, dict(lookX=.6, smile=1), {'base': {}}))
    S['B'] = dict(moca=sprite(pw, 'caB', cB, 'moca', 'moca', [1.55, 0, -1.2], -.7, dict(lookX=1), talk_states()),
                  rapaz=sprite(pw, 'caB', cB, 'rapaz', 'rapaz', [2.45, 0, -1.45], .7, dict(lookX=-1, smile=1), happy_states()),
                  local=sprite(pw, 'caB', cB, 'local', 'local', [4.15, 0, -0.55], -.6, dict(lookX=1), talk_states()),
                  senhor=sprite(pw, 'caB', cB, 'senhor', 'senhor', [4.95, 0, -0.8], .6, dict(lookX=-1, smile=1), happy_states()),
                  menino=sprite(pw, 'caB', cB, 'menino', 'menino', [3.2, 0, -2.3], .1, dict(smile=1), wave_states('w', 6, False, 'R', 1)))
    MAN['cais'] = dict(layers=out, sprites=S); save()
def bake_class(pw):
    lt = dict(useGround=0, Ldir=[-.7, .62, -.35], Lcol=[1.1, .95, .78], Acol=[.85, .78, .68], fogK=0., fogStart=50, tmaxU=40)
    cams = {'W': Cam([-.6, 1.55, -5.2], [-.4, 1.25, 6], 1.0), 'K': Cam([0.75, 1.75, 2.55], [1.6, .82, 4.2], 1.25)}
    out = {}
    for tag, cam in cams.items():
        base = dict(cam.args(), w=PW, h=H, **lt); L = {}
        lays = [(1, 'room', .45), (0, 'desk', .8)] + ([(2, 'fg', 1.8)] if tag == 'W' else [])
        for lay, nm, par in lays:
            fn = f'sala{tag}_{nm}.png'; render(pw, 'classroom.html', dict(base, layer=lay), f'{A}/{fn}')
            if nm == 'fg': blur(f'{A}/{fn}', f'{A}/{fn}', 16)
            L[nm] = dict(src=fn, par=par)
        out[tag] = L
    cW = cams['W']
    # posições da capa do livro e da lousa (para textos em perspectiva)
    cK = cams['K']; c = np.array([1.5, 0, 4.25]) + np.array([.12, .81 + .046, -.05]); a = .12
    def bk(dx, dz): return [c[0] + dx * math.cos(a) + dz * math.sin(a), c[1], c[2] - dx * math.sin(a) + dz * math.cos(a)]
    cover = [cK.proj(bk(sx, sz))[:2] for sx, sz in [(-.3, .2), (.3, .2), (.3, -.06), (-.3, -.06)]]
    board = [cW.proj(p)[:2] for p in [[-2.1, 2.45, 5.95], [1.5, 2.45, 5.95], [1.5, 1.15, 5.95], [-2.1, 1.15, 5.95]]]
    S = dict(prof=sprite(pw, 'sl', cW, 'prof', 'prof', [-0.8, 0, 4.85], -.1, dict(fwdR=.7, aR=.35, bR=.5), {'base': {}, 'open': dict(smile=1)}),
             a1=sprite(pw, 'sl', cW, 'a1', 'aluno1', [-1.5, 0, 1.05], math.pi, {}, {'base': {}}),
             a2=sprite(pw, 'sl', cW, 'a2', 'aluno2', [0., 0, 1.05], math.pi - .2, {}, {'base': {}}),
             a3=sprite(pw, 'sl', cW, 'a3', 'aluno3', [1.5, 0, 1.05], math.pi + .1, {}, {'base': {}}),
             canto=sprite(pw, 'sl', cW, 'canto', 'menino', [-2.75, 0, 5.45], math.pi - .25, dict(headN=1), {'base': {}}))
    MAN['sala'] = dict(layers=out, sprites=S, cover=cover, board=board); save()
def bake_maps(pw):
    # Caribe: varredura lateral de Aruba (x=-.57) a Bonaire (x=1.12)
    camC = Cam([0.25, 1.4, -1.3], [0.25, 0, -0.05], 1.3, pb=True)
    x0, x1 = -1.05, 1.42; Wc = int((x1 - x0) / camC.kk * H) + 2 * M
    camC.W = Wc; camC.ro[0] = camC.ta[0] = (x0 + x1) / 2
    o = dict(camC.args(), cyl=2, w=Wc, h=H, T=1., pin0=[-.57, .045, .52], pinH0=1, pin1=[.45, .045, .21], pinH1=1, pin2=[1.12, .035, .17], pinH2=1, boatOn=1, boatP=[.28, 0, -.12], boatA=.5)
    render(pw, 'map3d.html', o, f'{A}/mapa_caribe.png')
    lab = {k: camC.proj(p)[:2] for k, p in dict(aruba=[-.57, .26, .52], curacao=[.45, .26, .21], bonaire=[1.12, .25, .17], venezuela=[.3, 0, -.62]).items()}
    MAN['caribe'] = dict(src='mapa_caribe.png', W=Wc, labels=lab, xs={k: camC.proj(p)[0] for k, p in dict(aruba=[-.57, 0, .3], curacao=[.45, 0, .1], bonaire=[1.12, 0, .1]).items()})
    # Atlântico
    camA = Cam([0., 4., -1.25], [0., 0, .1], 1.9, pb=True)
    x0, x1 = -2.25, 1.35; Wa = int((x1 - x0) / camA.kk * H) + 2 * M
    camA.W = Wa; camA.ro[0] = camA.ta[0] = (x0 + x1) / 2
    geo = lambda la, lo: [(lo + 37) / 20, 0.0, (la - 2) / 20]
    o = dict(camA.args(), cyl=2, w=Wa, h=H, T=1.)
    render(pw, 'atl3d.html', o, f'{A}/mapa_atlantico.png')
    def curve(p0, p1, bend, n=60):
        p0, p1 = np.array(geo(*p0)), np.array(geo(*p1)); m = (p0 + p1) / 2 + np.array([0, 0, bend])
        return [camA.proj(list((1 - t) ** 2 * p0 + 2 * (1 - t) * t * m + t * t * p1))[:2] for t in np.linspace(0, 1, n)]
    MAN['atl'] = dict(src='mapa_atlantico.png', W=Wa,
        rotaAfrica=curve((8.0, -14.0), (12.2, -68.9), .35), rotaRecife=curve((-8.05, -34.88), (12.2, -68.9), -.05),
        labels={k: camA.proj(geo(*v))[:2] for k, v in dict(africa=(13, -12.5), recife=(-8.05, -34.88), curacao=(12.2, -68.9), brasil=(-1, -55), caribe=(16, -73)).items()})
    # barquinho (sprite): render só objetos
    for k, ang in [('barco', .0)]:
        bc = Cam([0, .55, -.9], [0, .02, 0], 1.3)
        render(pw, 'map3d.html', dict(bc.args(), w=360, h=360, objOnly=1, boatOn=1, boatP=[0, 0, 0], boatA=ang), f'{A}/{k}.png')
    save()
if __name__ == '__main__':
    what = sys.argv[1:] or ['all']
    with sync_playwright() as pw:
        if 'park' in what or 'all' in what: bake_park(pw)
        if 'water' in what or 'all' in what: bake_water(pw)
        if 'class' in what or 'all' in what: bake_class(pw)
        if 'maps' in what or 'all' in what: bake_maps(pw)
