"""Atores 3D (elenco com esqueleto) para as cenas do parque do ep2: cada ator vira uma camada própria (webp com alfa, recortada), com paralaxe pela profundidade.
uso: ep_actors.py [cena ...]   (cenas: A B C S)"""
import os, sys, json, math, subprocess, time
import numpy as np
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/opt/pw-browsers'
from playwright.sync_api import sync_playwright
from PIL import Image
T3 = '/home/claude/t3'; E = '/home/claude/holanda/ep2'; OUT = f'{E}/act'; os.makedirs(OUT, exist_ok=True)
PW, H, FPS = 1300, 1920, 30
CAST = json.load(open('/home/claude/holanda/ep_cast.json'))
face = lambda dx, dz: math.atan2(dx, dz)
camA = dict(camP=[0.3, 1.05, -8], camT=[0.3, 1.45, 10], span=1.25)
camB = dict(camP=[-1.7, 1.25, -7.2], camT=[1.3, 1.4, 10], span=1.25)
camC = dict(camP=[-1.0, 0.95, -6.5], camT=[-3.4, 6.0, 30], span=1.2)
DAY = dict(Ldir=[-.55, .62, -.45], light={})
SUN = dict(Ldir=[-.8, .32, -.35], light=dict(sunC=0xffb878, sunI=2.4, sky=0xffd8c0, gnd=0x7a5a50, hemi=1.35, rimC=0xffb070, rimI=1.6))
def act(who, keys, **fx): return dict(who=who, keys=keys, fx=fx)
SC = {
 'A': dict(t0=3.71, t1=8.68, cam=camA, **DAY, actors=[
   act('mae', [[0, -3.4, -0.5, face(1, 0), 'walk'], [3.0, -0.85, -0.5, face(1.77, -0.7), 'idle']], talk=[[3.3, 4.97]]),
   act('filho', [[0, -3.9, -1.2, face(1, 0), 'walk', .6], [3.4, -0.4, -1.2, face(1, -.25), 'idle', .8]]),
   act('filha', [[0, -2.9, -1.7, face(1, 0), 'walk', .3], [3.2, 0.1, -1.7, face(1.2, .25), 'idle', .4]]),
   act('guia', [[0, 1.05, -1.3, face(-1, -.3), 'idle', .4], [2.9, 1.05, -1.3, face(-1, -.45), 'agree'], [4.97, 1.05, -1.3, face(-1, -.45), 'agree']], smile=.6)]),
 'B': dict(t0=8.68, t1=12.9, cam=camB, **DAY, actors=[
   act('mae', [[0, -1.55, -4.6, face(1.15, 3.0), 'idle', .2]], par=1.5, blur=7),
   act('filha', [[0, -0.85, -2.75, face(.5, 1.1), 'idle', .9]]),
   act('guia', [[0, -0.4, -1.6, face(-.55, -1), 'idle', .4]], smile=.45, wave=[[1.67, 3.42, 'Right']], talk=[[.3, 1.2], [1.82, 2.52]])]),
 'C': dict(t0=12.9, t1=16.17, cam=camC, **DAY, actors=[
   act('filha', [[0, -1.5, -2.9, face(-.15, 1), 'idle']], hop=[[0, 3.27, .13, 2.3]], wave=[[0, 3.27, 'both']])]),
 'S': dict(t0=65.96, t1=75.6, cam=camA, **SUN, actors=[
   act('mae', [[0, -0.85, -0.5, face(.3, -1), 'idle', .2]], wave=[[6.59, 9.64, 'Right']]),
   act('filho', [[0, -0.45, -1.2, face(.25, -1), 'idle', .7]], wave=[[6.8, 9.64, 'Right']]),
   act('filha', [[0, 0.15, -1.75, face(-.15, -1), 'idle', 1.1]], wave=[[6.59, 9.64, 'Left']]),
   act('guia', [[0, 1.05, -1.3, face(-.6, -1), 'idle', .4]], smile=.6, wave=[[7.1, 9.64, 'Right']])]),
}

camWA = dict(camP=[0., 1.75, -8], camT=[0., 1.45, 10], span=1.25)
camWB = dict(camP=[3.4, 1.7, -7.8], camT=[2.6, 1.45, 10], span=1.25)
camSL = dict(camP=[-.6, 1.55, -5.2], camT=[-.4, 1.25, 6], span=1.0)
CAIS = dict(Ldir=[-.45, .75, -.5], light=dict(sunI=2.9))
SALA = dict(Ldir=[-.7, .62, -.35], light=dict(sunC=0xffe6c8, sunI=1.9, sky=0xfff2e2, gnd=0x8a6a50, hemi=1.7, rimI=.7))
alt = lambda a, b, d: [[x, min(x + 1.6, d)] for x in [a + 3.2 * i for i in range(5)] if x < d]
SC.update({
 'caA': dict(t0=25.7, t1=30.24, cam=camWA, **CAIS, actors=[
   act('senhor', [[0, -1.55, 0.6, face(.6, -1), 'idle', .3]], smile=.7),
   act('filha', [[0, 0.75, -1.9, face(-1, -.45), 'idle', .5]]),
   act('local', [[0, -0.6, -1.3, face(1.3, -.7), 'idle', .1]], smile=.5, talk=[[1.2, 2.9]], wave=[[.9, 2.6, 'Right']])]),
 'caB': dict(t0=55.65, t1=65.96, cam=camWB, **CAIS, actors=[
   act('menino', [[0, 0.9, -2.5, face(1, -.15), 'idle', .2], [4.0, 0.9, -2.5, face(1, -.15), 'walk', .2], [6.6, 3.35, -2.4, face(.2, -1), 'idle', .3]], wave=[[8.2, 9.6, 'Right']]),
   act('moca', [[0, 2.0, -1.2, face(.9, -.45), 'idle', .4]], talk=[[0, 1.8], [3.6, 5.6], [7.4, 9.2]]),
   act('rapaz', [[0, 2.75, -1.5, face(-.9, -.25), 'idle', 1.0], [1.9, 2.75, -1.5, face(-.9, -.25), 'idle', 1.0]], smile=.6, talk=[[1.9, 3.4], [5.8, 7.2], [9.4, 10.31]]),
   act('local', [[0, 4.0, -0.7, face(.8, -.45), 'idle', .7]], smile=.3, talk=[[.4, 2.6], [4.6, 6.4], [8.4, 10.31]]),
   act('senhor', [[0, 4.6, -0.95, face(-.8, -.2), 'idle', 1.3], [.8, 4.6, -0.95, face(-.8, -.2), 'agree'], [2.6, 4.6, -0.95, face(-.8, -.2), 'idle', .2], [4.8, 4.6, -0.95, face(-.8, -.2), 'agree'], [6.4, 4.6, -0.95, face(-.8, -.2), 'idle', .5]], smile=.7, talk=[[2.8, 4.4], [6.6, 8.2]])]),
 'slW': dict(t0=48.5, t1=55.65, cam=camSL, **SALA, actors=[
   act('canto', [[0, -2.75, 5.45, face(-.25, 1), 'idle', .2]], back=1),
   act('prof', [[0, -0.8, 4.85, face(.05, -1), 'idle', .5]], talk=[[.2, 3.9]], back=1),
   act('aluno1', [[0, -1.65, 1.05, face(0, 1), 'idle', .3]]),
   act('aluno2', [[0, -0.6, 1.05, face(-.2, 1), 'idle', .9]]),
   act('aluno3', [[0, 0.45, 1.05, face(.1, 1), 'idle', 1.4]])]),
})
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
                    fx = {k: v for k, v in a['fx'].items() if k not in ('par', 'blur', 'back')}
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
                    lst.append(dict(who=a['who'], x=bb[0], y=bb[1], w=cw, h=ch, par=par, blur=a['fx'].get('blur', 0), back=a['fx'].get('back', 0), frames=fr, z=depth(S['cam'], [k0[1], 0, k0[2]])))
                    print(tag, a['who'], n, 'quadros', round(time.time() - t), 's', flush=True)
                lst.sort(key=lambda d: -d['z']); man[tag] = dict(t0=S['t0'], actors=lst)
                json.dump(man, open(f'{OUT}/act.json', 'w'))
            b.close()
    finally:
        srv.terminate()
if __name__ == '__main__':
    run(sys.argv[1:] or list(SC))
