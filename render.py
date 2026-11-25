"""Render HTML (setT) -> MP4 via Chromium headless + ffmpeg.
python render.py stills 1.0 5.2 ...   |   python render.py scenes 0 1 2 ...   |   python render.py join"""
import os, sys, subprocess, json
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); FPS = 30
URL = "file://" + os.path.join(D, os.environ.get('PAGE','holanda.html'))
def page(p):
    b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--allow-file-access-from-files"])
    pg = b.new_page(viewport={"width": 1080, "height": 1920})
    pg.on("pageerror", lambda e: print("JS ERROR:", e))
    pg.goto(URL); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
    return b, pg
def shot(pg, T, path=None):
    pg.evaluate(f"setT({T})")
    return pg.screenshot(type="jpeg", quality=92, path=path)
if __name__ == "__main__":
    mode = sys.argv[1]
    with sync_playwright() as p:
        b, pg = page(p)
        if mode == "stills":
            for s in sys.argv[2:]: shot(pg, float(s), os.path.join(D, f"st_{s}.jpg"))
        elif mode == "scenes":
            bounds = pg.evaluate("SCENE_BOUNDS")
            for i in map(int, sys.argv[2:]):
                a, z = bounds[i]; n = round((z - a) * FPS); a0 = round(a * FPS)
                tmp = os.path.join(D, f"sc{i}.part.mp4")
                ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-c:v", "mjpeg", "-framerate", str(FPS), "-i", "-",
                     "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), "-f", "mp4", tmp], stdin=subprocess.PIPE)
                for k in range(n): ff.stdin.write(shot(pg, (a0 + k) / FPS))
                ff.stdin.close()
                if ff.wait() == 0: os.replace(tmp, os.path.join(D, f"sc{i}.mp4"))
                print("cena", i, "ok", flush=True)
        b.close()
