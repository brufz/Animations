import json,re,subprocess
raw=subprocess.run(["ffmpeg","-hide_banner","-i","narracao.mp3","-af","silencedetect=noise=-35dB:d=0.15","-f","null","-"],capture_output=True,text=True).stderr
st=[float(x) for x in re.findall(r"silence_start: ([0-9.]+)",raw)]; en=[float(x) for x in re.findall(r"silence_end: ([0-9.]+)",raw)]
gaps=list(zip(st,en))
S=[x[2] for x in json.load(open('align.json'))]
start=0.0; end=78.40
gaps=[g for g in gaps if g[1]<end]
speech=(end-start)-sum(b-a for a,b in gaps)
def real(x):  # tempo de fala acumulado -> tempo real
    cur=start;acc=0
    for a,b in gaps:
        if acc+(a-cur)>=x: return cur+(x-acc)
        acc+=a-cur;cur=b
    return cur+(x-acc)
L=[len(s) for s in S];T=sum(L);cum=0;est=[]
for l in L[:-1]: cum+=l; est.append(real(speech*cum/T))
mids=[(a+b)/2 for a,b in gaps]
# DP: escolher um gap crescente para cada fronteira
import math
n,m=len(est),len(mids);INF=1e9
D=[[INF]*m for _ in range(n)];B=[[-1]*m for _ in range(n)]
for j in range(m): D[0][j]=(est[0]-mids[j])**2
for i in range(1,n):
    best=INF;bj=-1
    for j in range(m):
        if j>0 and D[i-1][j-1]<best: best=D[i-1][j-1];bj=j-1
        if bj>=0: D[i][j]=best+(est[i]-mids[j])**2;B[i][j]=bj
j=min(range(m),key=lambda j:D[n-1][j]);sel=[0]*n
for i in range(n-1,-1,-1): sel[i]=j;j=B[i][j]
bnd=[start]+[mids[k] for k in sel]+[end]
out=[[round(bnd[i],2),round(bnd[i+1],2),S[i]] for i in range(len(S))]
for o in out: print(o)
json.dump(out,open('align2.json','w'),ensure_ascii=False)
