"""Renderiza elenco 3D (stage.html) sobre as placas do parque. uso: stage.py cena.json saida.mp4 [still.png]"""
import os, subprocess, time, json, sys
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/opt/pw-browsers'
from playwright.sync_api import sync_playwright
from PIL import Image
D = '/home/claude/t3'; E = '/home/claude/holanda/ep2'; O = f'{D}/stage'
S = json.load(open(sys.argv[1])); out = sys.argv[2]; still = sys.argv[3] if len(sys.argv) > 3 else None
PW, H, M = 1300, 1920, 110; N = S['N']
srv = subprocess.Popen(['python3', '-m', 'http.server', '8765', '--bind', '127.0.0.1'], cwd=D, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
try:
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = b.new_page(viewport={"width": PW, "height": H}); pg.on('pageerror', lambda e: print('ERR', e))
        pg.goto('http://127.0.0.1:8765/stage.html'); pg.wait_for_function("window.ok===1")
        pg.evaluate("o=>setup(o)", dict(S['cam'], w=PW, h=H, Ldir=S['Ldir'], actors=S['actors']))
        fr = [S.get('stillT', 0) * 30] if still else range(N)
        for i in fr:
            pg.evaluate("t=>frame(t)", i / 30); pg.locator('canvas').screenshot(path=f'{O}/a{int(i):03d}.png', omit_background=True)
        b.close()
finally:
    srv.terminate()
L = json.load(open(f'{E}/manifest.json'))['park']['layers'][S['plate']]
ld = lambda k: Image.open(f"{E}/{L[k]['src']}").convert('RGBA')
sky, far, near, fg = ld('sky'), ld('far'), ld('near'), ld('fg')
wheel = [Image.open(f'{E}/{f}').convert('RGBA') for f in L['wheel']['frames']]
def sh(im, dx):
    c = Image.new('RGBA', im.size); c.alpha_composite(im, (int(round(dx)), 0)); return c
def comp(i):
    T = i / 30; cx = S['pan'][0] + (S['pan'][1] - S['pan'][0]) * (i / max(1, N - 1))
    img = sh(sky, cx * .15); img.alpha_composite(sh(wheel[int(T * 7.6) % 16], cx * .22)); img.alpha_composite(sh(far, cx * .35)); img.alpha_composite(sh(near, cx * .75))
    img.alpha_composite(sh(Image.open(f'{O}/a{int(i):03d}.png').convert('RGBA'), cx * .9)); img.alpha_composite(sh(fg, cx * 1.9))
    return img.crop((M, 0, M + 1080, H)).convert('RGB')
if still:
    comp(int(S.get('stillT', 0) * 30)).save(still); sys.exit()
tmp = out[:-4] + '.tmp.mp4'
enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '30', '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
for i in range(N): comp(i).save(enc.stdin, 'JPEG', quality=92)
enc.stdin.close(); assert enc.wait() == 0; os.replace(tmp, out); print('ok', out)
