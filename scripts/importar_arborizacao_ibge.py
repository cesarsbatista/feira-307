#!/usr/bin/env python3
"""Censo 2022 IBGE: arborização nas vias por setor censitário de Belo Horizonte.
Arquivo original: GeoPackage oficial de dados percentuais do entorno dos domicílios.
Sem estimativas por bairro ou conversão do indicador em cobertura de copa.
"""
from __future__ import annotations
import json, sqlite3, pathlib, urllib.request, tempfile, math, re, os, sys, time
from shapely import wkb
from shapely.ops import transform as sh_transform
from pyproj import Transformer

ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'dados-externos'/'arborizacao.json'
URL='https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Dados_percentuais_das_Caracteristicas_urbanisticas_do_entorno_dos_domicilios/br_setores_entorno_cd2022.gpkg'
MUN='3106200'
K=10000000

def download(path):
  print('Baixando GPKG oficial',URL,flush=True)
  req=urllib.request.Request(URL,headers={'User-Agent':'Mozilla/5.0 (feira-307 pesquisa escolar)', 'Accept':'application/octet-stream,*/*'})
  with urllib.request.urlopen(req,timeout=240) as r, open(path,'wb') as f:
    total=0
    while True:
      chunk=r.read(2**20)
      if not chunk:break
      f.write(chunk);total+=len(chunk)
      if total%(64*2**20)<(2**20):print('Bytes recebidos',total,flush=True)
  if total<1000000:raise RuntimeError('Download incompleto')
  print('Download concluído:',total,'bytes',flush=True)

def merc(lon,lat):
  lat=max(-85,min(85,lat))
  return [round((lon+180)/360*K),round((1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*K)]

def qid(s):return '"'+s.replace('"','""')+'"'
def parse_num(x):
  if x is None or str(x).strip() in ('','-','...','X','x'):return None
  try:
    v=float(str(x).replace(',','.'))
    return v if math.isfinite(v) and 0<=v<=100 else None
  except (ValueError,TypeError):return None

def gpkg_wkb(data):
  if not isinstance(data,bytes) or data[:2]!=b'GP':raise ValueError('Geometria GPKG inválida')
  envelope=(data[3]>>1)&7
  n={0:0,1:32,2:48,3:48,4:64}.get(envelope)
  if n is None:raise ValueError('Envelope GeoPackage desconhecido')
  return wkb.loads(data[8+n:])

def normalize_polys(geom,transformer):
  geom=sh_transform(transformer.transform,geom)
  if not geom.is_valid:geom=geom.buffer(0)
  if geom.is_empty:return []
  # Mantém limites essenciais e remove excesso de vértices (aprox. 5 m na latitude de BH).
  geom=geom.simplify(.000035,preserve_topology=True)
  polys=([geom] if geom.geom_type=='Polygon' else list(geom.geoms) if geom.geom_type=='MultiPolygon' else [])
  result=[]
  for pol in polys:
    rings=[]
    for line in [pol.exterior,*pol.interiors]:
      pts=[merc(*xy[:2]) for xy in list(line.coords)]
      pts=[v for i,v in enumerate(pts) if not i or v!=pts[i-1]]
      if len(pts)>=4:rings.append(pts)
    if rings:result.append(rings)
  return result

def main():
  with tempfile.TemporaryDirectory() as td:
    f=pathlib.Path(td)/'ibge_entorno.gpkg'
    download(f)
    db=sqlite3.connect('file:'+str(f)+'?mode=ro',uri=True)
    db.row_factory=sqlite3.Row
    layers=list(db.execute("SELECT table_name,srs_id FROM gpkg_contents WHERE data_type='features'"))
    print('Camadas presentes:',[(x['table_name'],x['srs_id']) for x in layers],flush=True)
    if not layers:raise RuntimeError('GeoPackage sem tabelas espaciais')
    for item in layers:
      tab=item['table_name']
      cols=[x[1] for x in db.execute('PRAGMA table_info('+qid(tab)+')')]
      print('Campos IBGE: ',cols,flush=True)
      codecols=[c for c in cols if re.search('(^cd_setor|setor|cd_mun|cod_setor)',c,re.I)]
      code=next((c for c in cols if c.lower()=='cd_setor'),None)
      if code is None:raise RuntimeError('Chave CD_SETOR ausente da base IBGE')
      # Dicionário IBGE: V05230 = moradores em vias SEM árvores; V05200 = total com entorno pesquisado.
      # O campo oficial publicado V05200_V05230_PERC representa a parcela com pelo menos 1 árvore.
      # Não inferir por similaridade de nome: escolher a variável definida pelo IBGE.
      pctcol='v05200_v05230_perc'
      if pctcol not in cols:
        raise RuntimeError('Campo IBGE oficial de arborização ausente: '+pctcol)
      sample=list(db.execute('SELECT '+qid(code)+','+qid(pctcol)+',v05200_v05230 FROM '+qid(tab)+' WHERE CAST('+qid(code)+' AS TEXT) LIKE ? AND '+qid(pctcol)+' IS NOT NULL LIMIT 7',(MUN+'%',)))
      print('Amostra de arborização (setor, percentual, moradores em vias com árvores):',sample,flush=True)
      if len(sample)<5 or sum(parse_num(x[1]) is not None for x in sample)<5:
        raise RuntimeError('Coluna percentual de arborização do IBGE não validada para BH')
      geomcol=db.execute('SELECT column_name FROM gpkg_geometry_columns WHERE table_name=?',(tab,)).fetchone()[0]
      srs=int(db.execute('SELECT srs_id FROM gpkg_geometry_columns WHERE table_name=?',(tab,)).fetchone()[0])
      t=Transformer.from_crs('EPSG:'+str(srs),'EPSG:4326',always_xy=True)
      rows=db.execute('SELECT '+qid(code)+','+qid(pctcol)+','+qid(geomcol)+' FROM '+qid(tab)+' WHERE CAST('+qid(code)+' AS TEXT) LIKE ?',(MUN+'%',))
      features=[];non_null=0;bad=0;sectors=set()
      for cd,val,blob in rows:
        cd=str(cd or '')
        if len(cd)<12 or cd in sectors:continue
        sectors.add(cd)
        v=parse_num(val)
        if v is None:continue
        non_null+=1
        try:
          poly=gpkg_wkb(blob)
          for rings in normalize_polys(poly,t):
            pts=[pt for ring in rings for pt in ring]
            if not pts:continue
            box=[min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)]
            # Confere localização próxima de BH, sem aceitar geometrias fora da cidade.
            lon=(box[0]+box[2])/2/K*360-180
            lat=math.degrees(math.atan(math.sinh(math.pi*(1-(box[1]+box[3])/K))))
            if -44.35<lon<-43.55 and -20.20<lat<-19.60:
              features.append([box,rings,[cd,round(v,2)]])
        except Exception as e:
          bad+=1
          if bad<=5:print('Aviso geometria:',cd,str(e),flush=True)
      print('Belo Horizonte:',len(sectors),'setores identificados,',non_null,'percentuais,',len(features),'feições,',bad,'erros de geometria',flush=True)
      if non_null<900 or len(features)<900:
        raise RuntimeError('Quantidade de setores válida insuficiente, não publicar arquivo incompleto')
      if len(features)>20000:raise RuntimeError('Número inesperado de feições')
      out={
        'source':'IBGE — Censo Demográfico 2022, Pesquisa Urbanística do Entorno dos Domicílios',
        'reference':'Dados percentuais por setor censitário; publicação 12/12/2025; coleta de referência 2022',
        'url':URL,'count':len(features),'indicator':'Percentual de moradores em vias com pelo menos uma árvore (setor censitário)',
        'field':pctcol,'keyField':code,'spatialUnit':'setor censitário','validSectors':non_null,
        'method':'Percentual V05200_V05230_PERC publicado pelo IBGE: moradores em vias com pelo menos uma árvore. Sem agregação por bairro nem cálculos de cobertura de copa. Geometria simplificada para WebGIS.',
        'features':features
      }
      OUT.parent.mkdir(parents=True,exist_ok=True)
      tmp=OUT.with_suffix('.json.tmp')
      tmp.write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
      os.replace(tmp,OUT)
      print('PUBLICADO:',OUT.name,OUT.stat().st_size,'bytes',flush=True)
      return 0
    raise RuntimeError('Nenhuma camada espacial com chave de setor e variável de arborização validável.')
if __name__=='__main__':
  try:sys.exit(main())
  except Exception as e:print('ERRO NO IMPORTADOR:',repr(e),file=sys.stderr,flush=True);sys.exit(1)
