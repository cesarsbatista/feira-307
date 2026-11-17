#!/usr/bin/env python3
"""Gera um HTML V4 autônomo com as bases disponíveis no próprio repositório."""
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'index.html').read_text('utf-8')
geo=''.join((ROOT/'dados'/f'parte-{n:02}.txt').read_text('utf-8') for n in range(1,16))
json.loads(geo)
html,count=re.subn(r'^const DATA=JSON.parse\(\(await Promise\.all.*$',"const DATA=JSON.parse(document.getElementById('map-data').textContent);",html,count=1,flags=re.M)
if count!=1:raise RuntimeError('Trecho de dados originais não encontrado')
def inline(obj):
    return json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
official={}
for key in ('municipio','bairros','regionais','bacias','subbacias','arborizacao','indicadores_sociais'):
    path=ROOT/'dados-externos'/f'{key}.json'
    if path.exists():
        obj=json.loads(path.read_text('utf-8'))
        if isinstance(obj.get('features'),list) and obj['features']:official[key]=obj
html=html.replace('const EXT_KEYS=[','const OFFICIAL_DATA='+inline(official)+';\nconst EXT_KEYS=[',1)
i=html.index('async function loadExtraData(){')
start=html.index('const r=await fetch(',i)
end=html.index('const d=await r.json();',start)+len('const d=await r.json();')
html=html[:start]+"const d=OFFICIAL_DATA[id];if(!d)throw Error('camada fora do pacote offline');"+html[end:]
p=ROOT/'dados-externos'/'perfil_bairros.json'
profile=json.loads(p.read_text('utf-8')) if p.exists() else {}
html=html.replace('async function loadBairroProfiles(){','const OFFICIAL_PROFILE='+inline(profile)+';\nasync function loadBairroProfiles(){',1)
i=html.index('async function loadBairroProfiles(){')
start=html.index('const r=await fetch(',i)
end=html.index('const d=await r.json();',start)+len('const d=await r.json();')
html=html[:start]+'const d=OFFICIAL_PROFILE;'+html[end:]
tag='<script>\n(async()=>'
if tag not in html:raise RuntimeError('Script do aplicativo não encontrado')
html=html.replace(tag,'<script id="map-data" type="application/json">'+geo.replace('</','<\\/')+'</script>\n'+tag,1)
out=ROOT/'offline'/'Missao_Justica_Climatica_V4_OFFLINE.html'
out.parent.mkdir(exist_ok=True)
out.write_text(html,encoding='utf-8')
print('Offline:',out.stat().st_size,'bytes,',list(official),'camadas oficiais;',len(profile.get('bairros',[])),'registros populacionais')
