"""Alinha as linhas de legenda ao áudio usando as pausas (silencedetect) + DP; tempos por palavra proporcionais ao tamanho falado."""
import json, re, subprocess
L = [  # (legenda exibida, texto falado p/ estimar duração)
 ("*Dezenove gramas* de um pó azul.", None),
 ("Isso virou *seis mil toneladas* de lixo radioativo.", None),
 ("*Goiânia, 1987*.", "Goiânia, mil novecentos e oitenta e sete."),
 ("Uma clínica abandona um aparelho de *radioterapia*.", None),
 ("Dois catadores levam a peça, rompem o chumbo", None),
 ("e vendem a um *ferro-velho*.", None),
 ("À noite, o dono, *Devair*, vê um *brilho azul*.", None),
 ("E reparte com a família.", None),
 ("A sobrinha, *Leide*, de seis anos, brinca com o pó", None),
 ("e, no jantar, engole partículas.", None),
 ("A esposa, *Maria Gabriela*, leva a peça de ônibus à *Vigilância Sanitária*.", None),
 ("Um físico mede.", None),
 ("O número é tão alto que ele acha que o detector *quebrou*.", None),
 ("Pega outro. *Mesmo resultado*.", None),
 ("Aí vê um bombeiro saindo com a peça pra jogar no rio.", None),
 ("E grita: *pelo amor de Deus, não!*", None),
 ("Mais de *112 mil pessoas* são examinadas.", "Mais de cento e doze mil pessoas são examinadas."),
 ("*Leide* e *Maria Gabriela* morrem no mesmo dia.", None),
 ("No enterro, moradores atiram pedras.", None),
 ("O tratamento usou até um pigmento de tinta:", None),
 ("o *azul da Prússia*.", None),
 ("O lixo está em *Abadia de Goiás*,", None),
 ("guardado por *300 anos*.", "guardado por trezentos anos."),
 ("*Dezenove gramas*...", None),
 ("que o Brasil vai vigiar por *três séculos*.", None),
]
raw = subprocess.run(["ffmpeg", "-hide_banner", "-i", "cesio.mp3", "-af", "silencedetect=noise=-35dB:d=0.12", "-f", "null", "-"], capture_output=True, text=True).stderr
st = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", raw)]; en = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", raw)]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "cesio.mp3"], capture_output=True, text=True).stdout)
gaps = [(a, b) for a, b in zip(st, en) if a > 0.1 and b < dur - 0.05]
start = 0.0; end = st[-1] if st and st[-1] > dur - 1 else dur
spoken = [re.sub(r'[*~]', '', s if s2 is None else s2) for s, s2 in L]
speech = (end - start) - sum(b - a for a, b in gaps)
def real(x):
    cur = start; acc = 0
    for a, b in gaps:
        if acc + (a - cur) >= x: return cur + (x - acc)
        acc += a - cur; cur = b
    return cur + (x - acc)
W = lambda s: len(re.sub(r'[^\wÀ-ú]', '', s)) + 2.5 * len(re.findall(r'[.,:!?]', s))
LN = [W(s) for s in spoken]; T = sum(LN); cum = 0; est = []
for l in LN[:-1]: cum += l; est.append(real(speech * cum / T))
mids = [(a + b) / 2 for a, b in gaps]
n, m = len(est), len(mids); INF = 1e9
D = [[INF] * m for _ in range(n)]; B = [[-1] * m for _ in range(n)]
for j in range(m): D[0][j] = (est[0] - mids[j]) ** 2
for i in range(1, n):
    best = INF; bj = -1
    for j in range(m):
        if j > 0 and D[i - 1][j - 1] < best: best = D[i - 1][j - 1]; bj = j - 1
        if bj >= 0: D[i][j] = best + (est[i] - mids[j]) ** 2; B[i][j] = bj
j = min(range(m), key=lambda j: D[n - 1][j]); sel = [0] * n
for i in range(n - 1, -1, -1): sel[i] = j; j = B[i][j]
bnd = [start] + [mids[k] for k in sel] + [end]
out = []
for i, (s, s2) in enumerate(L):
    a, b = bnd[i], bnd[i + 1]
    if i > 0: a = gaps[sel[i - 1]][1] - 0.02
    if i < n: b = gaps[sel[i]][0] + 0.05
    words = re.sub(r'[*~]', '', s).split(); wl = [max(1.5, W(w)) for w in words]; tot = sum(wl); t = a; ws = []
    for w in wl: ws.append(round(t, 2)); t += (b - a - 0.05) * w / tot
    out.append([round(a, 2), round(b, 2), s, ws])
json.dump({"lines": out, "dur": dur}, open('timing.json', 'w'), ensure_ascii=False)
for o in out: print(f"{o[0]:6.2f} {o[1]:6.2f}  {o[2]}")
