"""Atores 3D (elenco com esqueleto) para as cenas do parque do ep2: cada ator vira uma camada própria (webp com alfa, recortada), com paralaxe pela profundidade.
uso: ep_actors.py [cena ...]   (cenas: A B C S)"""
import os, sys, json, math, subprocess, time
import numpy as np
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/opt/pw-browsers'
from playwright.sync_api import sync_playwright
from PIL import Image
T3 = '/home/claude/t3'; E = '/home/claude/cesio/ep3'; OUT = f'{E}/act'; os.makedirs(OUT, exist_ok=True)
PW, H, FPS = 1300, 1920, 30
CAST = json.load(open('/home/claude/cesio/cast3.json'))
MAN = json.load(open(f'{E}/manifest.json'))
face = lambda dx, dz: math.atan2(dx, dz)
def cam(n): return MAN[n]['cam']
DAY = dict(Ldir=[-.55, .62, -.45], light={})
DUSK = dict(Ldir=[-.8, .25, -.3], light=dict(sunC=0xffa070, sunI=1.6, sky=0x8a9ad8, gnd=0x6a5060, hemi=1.5, rimC=0x7fd0ff, rimI=1.4))
IN = dict(Ldir=[-.5, .7, -.5], light=dict(sunC=0xffe6c8, sunI=1.9, sky=0xfff2e2, gnd=0x8a6a50, hemi=1.7, rimI=.7))
NIGHT = dict(Ldir=[-.3, .9, -.4], light=dict(sunC=0xffd8a0, sunI=2.0, sky=0xffe8c8, gnd=0x7a5a40, hemi=1.5, rimC=0x7fd0ff, rimI=1.0))
def act(who, keys, **fx): return dict(who=who, keys=keys, fx=fx)
PECA = dict(type='cyl', size=[.24, .34, .24], color='#9aa0a8', metal=.6, rough=.35, rot=[0, 0, 1.5708], side='both', off=[0, .02, .08])
BARRA = dict(type='cyl', size=[.035, 1.0, .035], color='#5a4a3a', rot=[.3, 0, 0], side='Right', off=[0, -.1, .05])
SACOLA = dict(type='box', size=[.3, .3, .16], color='#8a5a3a', side='Right', off=[0, -.2, 0])
BRILHO = dict(type='sphere', size=[.07, .07, .07], color='#bfefff', emis='#5fd0ff', emisI=4, side='Right', off=[0, .03, .06])
DET1 = dict(type='box', size=[.13, .1, .2], color='#f2c14e', side='Right', off=[0, .02, .1])
DET2 = dict(type='box', size=[.13, .1, .2], color='#5a8fd8', side='Right', off=[0, .02, .1])
SC = {
 'clin2': dict(t0=12.6, t1=15.7, cam=cam('clin2'), **DAY, actors=[
   act('catador2', [[0, -5.0, 1.9, face(1, -.25), 'walk', .4], [3.1, -2.4, 1.2, face(1, -.25), 'walk', .4]], items=[BARRA]),
   act('catador1', [[0, -4.4, 1.0, face(1, -.25), 'walk'], [3.1, -1.7, .4, face(1, -.25), 'walk']], carry=[[0, 3.1, 'both']], items=[PECA])]),
 'ferro': dict(t0=15.7, t1=17.3, cam=cam('ferro'), **DAY, actors=[
   act('devair', [[0, .7, 1.3, face(-1, -.3), 'idle', .3], [.5, .7, 1.3, face(-1, -.3), 'agree']], smile=.6),
   act('catador1', [[0, -.6, 1.0, face(1, -.2), 'idle', .2]], carry=[[0, 1.6, 'both']], items=[PECA], talk=[[.1, 1.4]])]),
 'noite': dict(t0=17.3, t1=20.8, cam=cam('noite'), **NIGHT, actors=[
   act('devair', [[0, 1.75, 4.05, face(0, -1), 'idle', .6]], lookDown=.28, live=.5)]),
 'noite2': dict(t0=20.8, t1=22.4, cam=cam('noite2'), **NIGHT, actors=[
   act('maria', [[0, .55, 4.0, face(.5, -1), 'idle', .3]], carry=[[0, 1.6, 'Right', .1]], items=[BRILHO], smile=.5),
   act('devair', [[0, 1.75, 4.05, face(0, -1), 'idle', .6]], carry=[[0, 1.6, 'Right', .25]], items=[BRILHO], smile=.6),
   act('parente', [[0, 3.05, 4.1, face(-.5, -1), 'idle', 1.1]], smile=.6),
   act('menino', [[0, 2.85, 2.3, face(-.3, 1), 'idle', .9]], carry=[[0, 1.6, 'Right', .2]], items=[BRILHO])]),
 'coz1': dict(t0=22.4, t1=25.8, cam=cam('coz1'), **IN, actors=[
   act('leide', [[0, -.22, .02, face(.3, 1), 'idle', .4]], carry=[[0, 3.4, 'Right', -.05]], items=[dict(BRILHO, off=[0, .02, .05])], lookDown=.3, live=.6)]),
 'coz2': dict(t0=25.8, t1=28.1, cam=cam('coz2'), **IN, actors=[
   act('leide', [[0, -.6, .25, face(.7, .7), 'idle', .4]], lookDown=.22),
   act('lourdes', [[0, .3, 1.78, face(-.2, -1), 'idle', .8]], talk=[[.3, 1.4]]),
   act('parente', [[0, 1.45, .95, face(-1, .05), 'idle', 1.3]], talk=[[1.5, 2.3]])]),
 'onibus': dict(t0=28.1, t1=30.4, cam=cam('onibus'), **DAY, actors=[
   act('maria', [[0, -.45, -1.95, face(.5, -1), 'idle', .3]], lift=.42, live=.7)]),
 'vig': dict(t0=30.4, t1=32.6, cam=cam('vig'), **DAY, actors=[
   act('maria', [[0, 10.9, .45, face(1, .5), 'walk'], [2.2, 12.6, 1.35, face(1, .5), 'walk']], items=[SACOLA])]),
 'escr': dict(t0=32.6, t1=39.1, cam=cam('escr'), **IN, actors=[
   act('fisico', [[0, .25, 1.65, face(0, -1), 'idle', .4], [2.6, .25, 1.65, face(0, -1), 'hs'], [4.2, .25, 1.65, face(0, -1), 'idle', .2], [5.6, .25, 1.65, face(0, -1), 'hs']],
       carry=[[0, 4.05, 'Right', -.1], [4.55, 6.5, 'Right', -.1]], items=[dict(DET1, win=[0, 4.1]), dict(DET2, win=[4.5, 6.5])], lookDown=.2)]),
 'vig2': dict(t0=39.1, t1=44.6, cam=cam('vig'), **DAY, actors=[
   act('bombeiro', [[0, 12.9, 1.7, face(.75, -.65), 'walk'], [3.3, 14.3, .5, face(.75, -.65), 'idle'], [3.9, 14.3, .5, face(-.9, -.4), 'idle']], items=[SACOLA]),
   act('fisico', [[0, 12.5, 1.75, face(.5, -1), 'idle', .3]], vis=[3.0, 5.6], wave=[[3.75, 5.5, 'Right']], talk=[[3.8, 5.4]])]),
 'estadio': dict(t0=44.6, t1=48.1, cam=cam('estadio'), **DAY, actors=[
   act('povo2', [[0, -2.1, .3, face(1, -.1), 'idle', .2]]),
   act('povo3', [[0, -1.4, .35, face(1, -.1), 'idle', .9]]),
   act('povo4', [[0, -.8, .3, face(1, -.2), 'idle', 1.5]]),
   act('povo1', [[0, .3, .6, face(1, -.3), 'idle', .5]]),
   act('medico', [[0, 1.25, .9, face(-1, -.35), 'idle', 1.1]], carry=[[0, 3.5, 'Right', -.2]], items=[DET1], talk=[[.8, 2.2]])]),
 'enterro': dict(t0=51.1, t1=53.7, cam=cam('enterro'), **DAY, actors=[
   act('devair', [[0, 5.0, .9, face(0, 1), 'idle', .3]], lookDown=.3, live=.4),
   act('lourdes', [[0, 3.95, 1.15, face(.35, 1), 'idle', .9]], lookDown=.3, live=.4),
   act('parente', [[0, 6.1, 1.3, face(-.35, 1), 'idle', 1.4]], lookDown=.3, live=.4)]),
}
def depth(cam, P):
    ro = np.array(cam['camP'], float); ww = np.array(cam['camT'], float) - ro; ww /= np.linalg.norm(ww)
    return float((np.array(P, float) - ro) @ ww)
def run(tags):
    man = json.load(open(f'{OUT}/act.json')) if os.path.exists(f'{OUT}/act.json') else {}
    srv = subprocess.Popen(['python3', '-m', 'http.server', '8765', '--bind', '127.0.0.1'], cwd=T3, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
            for tag in tags:
                S = SC[tag]; n = round((S['t1'] - S['t0']) * FPS); lst = []
                for a in S['actors']:
                    t = time.time()
                    pg = b.new_page(viewport={"width": PW, "height": H}); pg.on('pageerror', lambda e: print('ERR', e))
                    pg.goto('http://127.0.0.1:8765/stage.html'); pg.wait_for_function("window.ok===1")
                    fx = {k: v for k, v in a['fx'].items() if k not in ('par', 'blur', 'back', 'vis')}
                    pg.evaluate("o=>setup(o)", dict(S['cam'], w=PW, h=H, Ldir=S['Ldir'], light=S['light'], actors=[dict(spec=CAST[a['who']], keys=a['keys'], fx=fx)]))
                    ims = []
                    for i in range(n):
                        pg.evaluate("t=>frame(t)", i / FPS)
                        ims.append(Image.open(__import__('io').BytesIO(pg.locator('canvas').screenshot(omit_background=True))).convert('RGBA'))
                    pg.close()
                    bb = None
                    for im in ims:
                        q = im.getchannel('A').getbbox()
                        if q: bb = q if bb is None else (min(bb[0], q[0]), min(bb[1], q[1]), max(bb[2], q[2]), max(bb[3], q[3]))
                    pad = 24; bb = (max(0, bb[0] - pad), max(0, bb[1] - pad), min(PW, bb[2] + pad), min(H, bb[3] + pad))
                    fr = []
                    cw, ch = bb[2] - bb[0], bb[3] - bb[1]
                    for i, im in enumerate(ims):
                        fn = f'act/{tag}_{a["who"]}_{i:03d}.webp'; im.crop(bb).save(f'{E}/{fn}', 'WEBP', quality=88, method=4); fr.append(fn)
                    k0 = a['keys'][0]; par = a['fx'].get('par') or round(min(2.2, 7.5 / depth(S['cam'], [k0[1], 0, k0[2]])), 3)
                    lst.append(dict(who=a['who'], x=bb[0], y=bb[1], w=cw, h=ch, par=par, blur=a['fx'].get('blur', 0), back=a['fx'].get('back', 0), vis=a['fx'].get('vis'), frames=fr, z=depth(S['cam'], [k0[1], 0, k0[2]])))
                    print(tag, a['who'], n, 'quadros', round(time.time() - t), 's', flush=True)
                lst.sort(key=lambda d: -d['z']); man[tag] = dict(t0=S['t0'], actors=lst)
                json.dump(man, open(f'{OUT}/act.json', 'w'))
            b.close()
    finally:
        srv.terminate()
if __name__ == '__main__':
    run(sys.argv[1:] or list(SC))
