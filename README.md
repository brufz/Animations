# E se...? — animações híbridas 2.5D por código

Motor usado nos vídeos do canal **"E se...?"** (história alternativa com fatos reais), vertical 1080×1920, 30 fps.

- **Cenários em 2.5D:** HTML + SVG em camadas com profundidade (Z), câmera 3D real via CSS 3D (`perspective`), desfoque de foco, névoa e sombras entre camadas.
- **Personagens em 3D:** renderizador próprio em WebGL (raymarching com formas simples — cápsulas, esferas, cilindros), com luz, sombra e oclusão. Cada personagem vira uma sequência de quadros em PNG transparente (`sprites/`).
- **Animação determinística:** tudo é calculado por `setT(tempo)` — sem animações CSS soltas.
- **Render:** Chromium headless (Playwright) fotografa quadro a quadro; `ffmpeg` codifica cada cena e junta tudo com a narração.

## Estrutura

| Arquivo | O que é |
|---|---|
| `papiamento.html` | Episódio 2 — Hopi Hari e o papiamento (parque, mapa do Caribe, Atlântico, sala de aula) |
| `holanda.html` | Episódio 1 — "E se os holandeses nunca tivessem saído do Nordeste?" (cenas, legendas, HUD) |
| `render.py` | Renderiza quadros-chave e cenas em MP4 |
| `align.py` | Alinha as frases do roteiro às pausas da narração (sincronia de cenas e legendas) |
| `chars3d.html` + `sprites.py` | Biblioteca de personagens 3D e o script que gera os sprites |
| `sprites/` | Sprites prontos: moradores (10 variações), soldado, Nassau, pintor, jogador, boi |
| `roteiros/` | Roteiros dos episódios (texto da narração) |
| `testes/` | Testes de estilo (máquina do tempo, livro pop-up, rua 100% 3D, boneco 3D) |
| `noise.png` | Textura de granulação |

## Requisitos

- Python 3 com `playwright`, `numpy`, `Pillow`
- Chromium do Playwright (`playwright install chromium`)
- `ffmpeg`
- Fonte Roboto variável (o HTML aponta para `/usr/share/fonts/truetype/google-fonts/ofl/roboto/Roboto[wdth,wght].ttf` — ajuste o `@font-face` se estiver em outro lugar)

## Como gerar um episódio

```bash
# 1) quadros-chave para conferir (gera st_<tempo>.jpg)
python render.py stills 2 10 25 50

# 2) cenas em paralelo (gera sc<N>.mp4)
python render.py scenes 0 2 4 6 8 10 12 14 &
python render.py scenes 1 3 5 7 9 11 13
wait

# 3) juntar e colocar a narração
for i in $(seq 0 14); do echo "file 'sc$i.mp4'"; done > list.txt
ffmpeg -f concat -safe 0 -i list.txt -c copy video_mudo.mp4
ffmpeg -i video_mudo.mp4 -i narracao.mp3 -map 0:v -map 1:a -c:v libx264 -crf 23 \
       -pix_fmt yuv420p -c:a aac -b:a 192k -af apad -shortest -movflags +faststart episodio.mp4
```

Outra página: `PAGE=testes/teste_tempo.html python render.py scenes 0`

## Fluxo de cada episódio

1. Ideias "E se...?" com nota para gancho, visual e número verificável
2. Checagem de fatos com fontes (lenda = "diz a lenda"; especulação = "talvez")
3. Roteiro em batidas (~2,4 palavras/s, 70–85 s para passar de 1 minuto)
4. Narração no ElevenLabs (`eleven_v4`, voz "Fernando Will"), números por extenso
5. `align.py` para sincronizar; cenas e legendas acompanham a fala
6. Render + conferência de quadros-chave
