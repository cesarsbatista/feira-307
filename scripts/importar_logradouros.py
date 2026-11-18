#!/usr/bin/env python3
"""Baixa e prepara cadastro oficial de trechos de logradouro PBH para busca local.

Exige serviço WFS disponível. Não grava arquivos incompletos em caso de falha.
"""
import json, math, os, re, time, unicodedata, urllib.parse, urllib.request
from collections import defaultdict
from pathlib import Path

SERVICE="https://bhmap.pbh.gov.br/v2/api/idebhgeo/wfs"
OUT=Path("dados-externos/logradouros")
PAGE=4000
LIMIT=70
K=10000000

def normalize(name):
    text=unicodedata.normalize("NFD", str(name)).encode("ascii","ignore").decode().lower()
    text=re.sub(r"[^a-z0-9]+"," ",text).strip()
    return re.sub(r"^(rua|avenida|alameda|travessa|praca|beco|estrada|rodovia) ","",text)

def webmerc(pt):
    lon,lat=float(pt[0]),float(pt[1])
    if not(-45<lon<-42 and -21<lat<-18):
        raise ValueError("Geometria inesperada: verifique o SRS da resposta WFS")
    return [round((lon+180)/360*K),round((1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*K)]

def paths(g):
    typ=g.get("type")
    if typ=="LineString": return [g["coordinates"]]
    if typ=="MultiLineString": return g["coordinates"]
    return []

def request(start):
    args=dict(service="WFS",version="2.0.0",request="GetFeature",
              typeNames="ide_bhgeo:TRECHO_LOGRADOURO",outputFormat="application/json",
              srsName="EPSG:4326",count=str(PAGE),startIndex=str(start))
    url=SERVICE+"?"+urllib.parse.urlencode(args)
    last=None
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"RaizesDesigualdade/1.0 (educational project)","Accept":"application/json"})
            with urllib.request.urlopen(req,timeout=75) as r:
                obj=json.load(r)
            if not isinstance(obj.get("features"),list):
                raise ValueError("WFS não respondeu com GeoJSON")
            return obj
        except Exception as e:
            last=e
            time.sleep((attempt+1)*3)
    raise RuntimeError("WFS indisponível: "+str(last))

def main():
    groups=defaultdict(lambda:{"name":"","lines":[]})
    seen=set()
    total=0
    for page in range(LIMIT):
        result=request(page*PAGE)
        features=result["features"]
        if not features: break
        added=0
        for feat in features:
            prop={k.upper():v for k,v in (feat.get("properties") or {}).items()}
            ident=prop.get("ID_LOGRADOURO")
            n=prop.get("NOME_LOGRADOURO")
            if ident is None or not n: continue
            key=str(ident)
            grp=groups[key]
            prefix=str(prop.get("DESC_SIGLA_TIPO_LOGRAD") or prop.get("SIGLA_TIPO_LOGRADOURO") or "").strip()
            grp["name"]=(" ".join((prefix,str(n)))).strip()
            fid=str(prop.get("ID_TRECHO_LOGRADOURO") or feat.get("id") or "")
            if fid and fid in seen:continue
            if fid:seen.add(fid)
            for raw in paths(feat.get("geometry") or {}):
                line=[webmerc(p) for p in raw]
                if len(line)<2: continue
                # Keep all official segments and their endpoints.
                grp["lines"].append(line)
                added+=1
        total+=len(features)
        print("Page",page+1,"received",len(features),"segments",added,flush=True)
        if len(features)<PAGE:break
    else:
        raise RuntimeError("Limite de paginação atingido: exportação incompleta")
    if total<5000 or len(groups)<500:
        raise RuntimeError("Exportação inesperadamente pequena; não publicar")
    index=defaultdict(list)
    shards=[{} for _ in range(32)]
    for ident,grp in groups.items():
        if not grp["lines"]:continue
        key=normalize(grp["name"])
        if not key: continue
        part=int(ident)%32 if ident.isdigit() else sum(map(ord,ident))%32
        shards[part][ident]=grp["lines"]
        index[key].append([ident,part,grp["name"]])
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"index.json").write_text(json.dumps({"source":"PBH/Prodabel — TRECHO_LOGRADOURO","groups":sum(map(len,shards)),"streets":index},ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    for i,shard in enumerate(shards):
        (OUT/f"parte-{i:02d}.json").write_text(json.dumps(shard,separators=(",",":")),encoding="utf-8")
    print("Complete:",total,"features,",len(groups),"logradouro IDs")

if __name__=="__main__":main()
