# Episódio 2 — Papiamento (v3, estilo 2.5D com cenários 3D)

Pipeline:
1. `mapdata.py` / `atl.py` — geram as texturas de relevo dos mapas a partir de contornos reais (lat/lon).
2. `bake.py` — renderiza os cenários 3D (raymarching SDF em WebGL: `park3.html`, `waterfront.html`, `classroom.html`, `map3d_src.html`) em camadas (fundo / meio / primeiro plano desfocado) e os bonecos (`chars_v2.html`) com piscar, falar e acenar. Saída: `ep2/` + `manifest.json`.
3. `build_ep2.py` — monta `ep2.html`: camadas com parallax lateral (sem zoom), sprites animados, legendas sincronizadas, HUD.
4. `render2.py scenes 0..9` (PAGE=ep2.html) → MP4 por cena; concat + áudio.

Regras de estilo aprendidas: câmera parada ou deslizando de lado; 3 camadas de profundidade; personagens grandes; mapas como maquete com desfoque de miniatura nas bordas; nada de zoom constante, placas grandes ou cartões de palavras.
