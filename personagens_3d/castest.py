import os, subprocess, time, sys, json
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/opt/pw-browsers'
from playwright.sync_api import sync_playwright
D = '/home/claude/t3'
specs = json.load(open(sys.argv[1])); out = sys.argv[2]
srv = subprocess.Popen(['python3', '-m', 'http.server', '8765', '--bind', '127.0.0.1'], cwd=D, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
try:
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = b.new_page(viewport={"width": 1600, "height": 760}); pg.on('pageerror', lambda e: print('ERR', e))
        pg.goto('http://127.0.0.1:8765/castest.html'); pg.wait_for_function("window.ok===1")
        pg.evaluate("o=>setup(o)", dict(w=1600, h=760, camP=[0, 1.05, 8.2], camT=[0, .95, 0], fov=28))
        n = len(specs)
        for i, s in enumerate(specs):
            x = (i - (n - 1) / 2) * 1.05
            print(s['spec']['model'], pg.evaluate("a=>add(...a)", [s['spec'], x, s.get('k'), s.get('t', 0), s.get('rot', 0)])[:300])
        pg.evaluate("()=>snap()"); pg.screenshot(path=out); b.close()
finally:
    srv.terminate()
