#!/usr/bin/env python3
"""Gera HTML autônomo com as camadas municipais importadas."""
import json
import pathlib
import re
ROOT = pathlib.Path(__file__).resolve().parents[1]
html = (ROOT / 'index.html').read_text(encoding='utf-8')
geo = ''.join((ROOT / 'dados' / f'parte-{n:02}.txt').read_text(encoding='utf-8') for n in range(1,16))
json.loads(geo)
original = html
html = re.sub(r'^const DATA=JSON.parse\(\(await Promise\.all.*$', "const DATA=JSON.parse(document.getElementById('map-data').textContent);", html, count=1, flags=re.M)
if original==html: raise RuntimeError('Expressão DATA não localizada')
official = {}
for key in ('bairros', 'regionais', 'bacias', 'subbacias'):
    p = ROOT / 'dados-externos' / f'{key}.json'
    if p.exists():
        official[key] = json.loads(p.read_text(encoding='utf-8'))
marker='const EXT_KEYS=['
assert marker in html
html=html.replace(marker,'const OFFICIAL_DATA='+json.dumps(official,ensure_ascii=False,separators=(',',':'))+';\n'+marker,1)
start=html.index('async function loadExtraData(){')
a=html.index('const r=await fetch(',start)
b=html.index('const d=await r.json();',a)+len('const d=await r.json();')
html=html[:a]+"const d=OFFICIAL_DATA[id];if(!d)throw Error('camada não incluída na versão offline');"+html[b:]
main_start=html.find('<script>\n(async()=>')
if main_start<0:raise RuntimeError('Script principal não localizado')
html=html[:main_start]+'<script id="map-data" type="application/json">'+geo+'</script>\n'+html[main_start:]
OUT=ROOT/'offline'/'Missao_Justica_Climatica_V3_OFFLINE.html'
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(html,encoding='utf-8')
print(f'HTML offline gerado: {OUT} ({OUT.stat().st_size} bytes); bases oficiais: {list(official)}')
