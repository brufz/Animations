"""Trilha + efeitos sonoros sintetizados para o ep3, com 'ducking' sob a narração. Saída: mix3.wav (48 kHz estéreo)"""
import numpy as np, subprocess, json
from scipy import signal
SR = 48000; DUR = 66.7; N = int(SR * DUR); rng = np.random.default_rng(7)
t = np.arange(N) / SR
def mono(): return np.zeros(N)
def env_seg(a, b, att=.3, rel=.5):
    e = np.zeros(N); i0, i1 = int(a * SR), int(min(b, DUR) * SR); x = np.arange(i1 - i0) / SR
    e[i0:i1] = np.minimum(1, np.minimum(x / max(att, 1e-3), (b - a - x) / max(rel, 1e-3))).clip(0, 1); return e
def lp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'high', fs=SR, output='sos'), x)
def bp(x, a, b, o=2): return signal.sosfilt(signal.butter(o, [a, b], 'band', fs=SR, output='sos'), x)
def place(dst, snd, at, g=1.):
    i = int(at * SR); n = min(len(snd), N - i)
    if n > 0: dst[i:i + n] += snd[:n] * g
def noise(sec): return rng.normal(size=int(sec * SR))
def boom(sec=1.8, f0=70, f1=32):
    x = np.arange(int(sec * SR)) / SR; f = f1 + (f0 - f1) * np.exp(-x * 6); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-x * 2.2) + lp(noise(sec), 300) * .25 * np.exp(-x * 8)
def whoosh(sec=.5):
    x = np.arange(int(sec * SR)) / SR; n = noise(sec); out = np.zeros_like(n)
    for k in range(8):
        a, b = int(k / 8 * len(n)), int((k + 1) / 8 * len(n)); fc = 400 + 3000 * (k / 8)
        out[a:b] = bp(n, fc * .7, fc * 1.3)[a:b]
    return out * np.sin(np.pi * x / sec) ** 2
def click(): x = np.arange(int(.004 * SR)) / SR; return hp(noise(.004), 2500) * np.exp(-x * 1500)
def bell(f=440, sec=4.):
    x = np.arange(int(sec * SR)) / SR; return sum(np.sin(2 * np.pi * f * r * x) * np.exp(-x * d) * a for r, d, a in [(1, .9, 1), (2.76, 1.6, .5), (5.4, 2.6, .25), (8.9, 4, .12)])
def clank(f=310, sec=1.2):
    x = np.arange(int(sec * SR)) / SR; return sum(np.sin(2 * np.pi * f * r * x) * np.exp(-x * (5 + 3 * i)) * a for i, (r, a) in enumerate([(1, 1), (1.47, .7), (2.31, .5), (3.9, .3)])) + hp(noise(sec), 2000) * np.exp(-x * 40) * .5
def thud(): x = np.arange(int(.35 * SR)) / SR; return lp(noise(.35), 220) * np.exp(-x * 18) * 2 + hp(noise(.35), 1500) * np.exp(-x * 60) * .3
# ---------------- MÚSICA
mus = mono()
def note(f): return 440 * 2 ** ((f - 69) / 12)
# drone
drone = (np.sin(2 * np.pi * 55 * t) * .6 + lp(signal.sawtooth(2 * np.pi * 110.3 * t), 400) * .3) * (.75 + .25 * np.sin(2 * np.pi * .08 * t))
mus += drone * (env_seg(0.3, 48.3, .8, 1.2) * .9 + env_seg(48.1, 53.9, 1, 1) * .45 + env_seg(53.7, 66.7, 1.5, 2) * .8)
# pad de acordes (Am, F, Dm, E) – 3,33 s cada; no laboratório vira maior (C, G)
prog_m = [[57, 60, 64], [53, 57, 60], [50, 53, 57], [52, 56, 59]]; prog_M = [[48, 55, 64], [55, 59, 62]]
pad = mono(); L = 3.333
for k in range(int(DUR / L) + 1):
    a = k * L; ch = prog_M[k % 2] if 53.5 <= a < 62 else prog_m[k % 4]
    seg = env_seg(a, a + L + .4, 1.2, 1.2)
    for m in ch:
        f = note(m); pad += seg * (signal.sawtooth(2 * np.pi * f * t) + signal.sawtooth(2 * np.pi * f * 1.006 * t)) * .5
pad = lp(pad, 900, 2) * .22
mus += pad * (env_seg(2.3, 66.7, 1.5, 3))
# pulso (batida grave) 72 bpm, mais denso na parte da tensão
pulse = mono(); kick = boom(.5, 95, 45) * .7; per = 60 / 72
for b in np.arange(2.45, 48.1, per): place(pulse, kick, b, 1.0 if b < 32.6 else 1.25)
for b in np.arange(32.6, 44.6, per / 2): place(pulse, hp(noise(.05), 6000) * np.exp(-np.arange(int(.05 * SR)) / SR * 90), b + per / 4, .25)
for b in np.arange(53.7, 62.2, per * 2): place(pulse, kick, b, .55)
mus += lp(pulse, 2000) * .55
# brilho (shimmer) nas cenas do pó azul
sh = sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate([1975, 2349, 2637, 3136])) * (.5 + .5 * np.sin(2 * np.pi * 5.3 * t)) * .05
mus += sh * (env_seg(0.3, 2.6, .2, .4) + env_seg(17.3, 28.2, .8, .8) * .7 + env_seg(62.2, 66.7, .6, 2.))
# ---------------- EFEITOS
fx = mono()
# abertura: subida + estouro azul
x = np.arange(int(.35 * SR)) / SR; rise = bp(noise(.35), 800, 6000) * (x / .35) ** 2; place(fx, rise, 0, .5)
place(fx, boom(2.2, 80, 30), .33, 1.1); place(fx, hp(noise(1.2), 3000) * np.exp(-np.arange(int(1.2 * SR)) / SR * 4), .33, .35)
# transições
CUTS = [2.45, 6.4, 9.4, 12.6, 15.7, 17.3, 20.8, 22.4, 25.8, 28.1, 30.4, 32.6, 39.1, 44.6, 48.1, 51.1, 53.7, 57.8, 62.2]
for c in CUTS: place(fx, whoosh(.45), c - .25, .22)
# números
for a in [3.0, 45.0]: place(fx, boom(1.6, 75, 35), a, .8)
place(fx, boom(2.5, 60, 28), 63.9, .9)
# pino do mapa
pl = bell(1320, .8) * .5; place(fx, pl, 7.2, .35)
# vento (clínica, depósito)
wind = lp(noise(DUR), 500) * (.6 + .4 * np.sin(2 * np.pi * .3 * t)); fx += wind * (env_seg(9.4, 12.8, .6, .6) + env_seg(57.8, 62.3, .8, .8)) * .12
# rompem o chumbo
place(fx, clank(300), 13.95, .5); place(fx, clank(260), 14.35, .45)
# ferro-velho de dia: ruído metálico leve
place(fx, clank(520, .8), 16.3, .18)
# grilos à noite
cr = mono()
for a in np.arange(17.3, 22.4, .45):
    x = np.arange(int(.12 * SR)) / SR; ch = np.sin(2 * np.pi * 4300 * x) * (np.sin(2 * np.pi * 30 * x) > 0) * np.sin(np.pi * x / .12)
    place(cr, ch, a + rng.uniform(0, .1), rng.uniform(.5, 1))
fx += cr * .05
# zumbido do brilho
hum = (np.sin(2 * np.pi * 60 * t) + .5 * np.sin(2 * np.pi * 120 * t) + .25 * np.sin(2 * np.pi * 180 * t)); fx += hum * (env_seg(17.6, 22.4, 1, .5) + env_seg(22.4, 28.1, .5, .8) * .6) * .05
# pratos no jantar
place(fx, bell(2200, .6) * .4, 26.4, .2); place(fx, bell(2600, .5) * .4, 26.9, .15)
# ônibus passando (pan esquerda -> direita)
bus = lp(noise(2.6), 180) * 1.5 + lp(signal.sawtooth(2 * np.pi * 38 * np.arange(int(2.6 * SR)) / SR), 300) * .4
bus *= np.sin(np.pi * np.arange(len(bus)) / len(bus)) ** 1.5
busL, busR = mono(), mono(); pan = np.linspace(0, 1, len(bus))
place(busL, bus * (1 - pan), 28.0, .6); place(busR, bus * pan, 28.0, .6)
# contador Geiger
gg = mono()
def geiger(a, b, r0, r1, ramp):
    tt = a
    while tt < b:
        rate = r0 + (r1 - r0) * min(1, (tt - a) / ramp); tt += rng.exponential(1 / rate); place(gg, click(), tt, rng.uniform(.6, 1))
geiger(33.2, 36.9, 2, 70, 1.4); geiger(37.5, 39.0, 4, 80, .8)
fx += gg * .9
# grito: impacto
place(fx, boom(1.2, 110, 50), 42.95, .7)
# murmúrio da multidão
mur = sum(bp(noise(DUR), f * .85, f * 1.15) * (.5 + .5 * np.sin(2 * np.pi * (1.3 + i * .7) * t + i)) for i, f in enumerate([350, 520, 800, 1150])); fx += mur * env_seg(44.6, 48.2, .5, .6) * .06
# sino no memorial
place(fx, bell(392, 5.), 48.35, .25)
# pedras
for i in range(9): place(fx, thud(), 51.1 + .35 + i * .22 + .55, .7 * rng.uniform(.6, 1))
# final
place(fx, boom(3.0, 55, 25), 65.3, .7)
# ---------------- MIXAGEM com ducking
voz, _ = None, None
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', 'cesio.mp3', '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
voz = np.frombuffer(raw, np.float32).astype(float); voz = np.pad(voz, (0, max(0, N - len(voz))))[:N]
venv = lp(np.abs(voz), 6, 1); venv = venv / (venv.max() + 1e-9); duck = 1 - .55 * np.clip(venv * 4, 0, 1)
def norm(x, peak): return x / (np.abs(x).max() + 1e-9) * peak
mus = norm(mus, .30) * duck
fxm = norm(fx, .55)
L_ = voz * .95 + mus + fxm * .9 + busL * .5
R_ = voz * .95 + mus * .97 + fxm * .9 + busR * .5
# pequena largura estéreo para a música
d = int(.012 * SR); R_ = R_ + np.concatenate([np.zeros(d), mus[:-d]]) * .15
st = np.stack([L_, R_], 1); st *= .95 / np.abs(st).max()
from scipy.io import wavfile
wavfile.write('mix3.wav', SR, (st * 32767).astype(np.int16)); print('ok', np.abs(voz).max())
