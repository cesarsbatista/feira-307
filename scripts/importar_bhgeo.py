#!/usr/bin/env python3
"""Importador de geometrias abertas da Prefeitura de Belo Horizonte, sem dados inventados.
Prefere WFS oficial atualizado. KMZ histórico da própria PBH é opção de contingência.
"""
import io
import json
import math
import pathlib
import urllib.parse
import urllib.request
import zipfile
from xml.etree import ElementTree as ET

OUT = pathlib.Path(__file__).resolve().parents[1] / 'dados-externos'
OUT.mkdir(parents=True, exist_ok=True)
SERVICES = ['https://geoservicos.pbh.gov.br/geoserver/wfs',
            'https://bhmap.pbh.gov.br/v2/api/idebhgeo/wfs']
KMZ_BASE = 'https://prefeitura.pbh.gov.br/sites/default/files/estrutura-de-governo/governo/documentos/'
TARGETS = {
 'bairros': (['BAIRRO_OFICIAL','BAIRRO'], 'Bairros_2014.kmz', '2014 — arquivo histórico de consulta'),
 'regionais': (['REGIONAL'], 'regionais_administrativas.kmz', '2018 ou anterior — arquivo de consulta'),
 'bacias': (['BACIA_HIDROGRAFICA','BACIA'], 'Macrobacias.kmz', '2018 ou anterior — Plano Municipal de Saneamento'),
 'subbacias': (['SUB_BACIA_HIDROGRAFICA','SUBBACIA_HIDROGRAFICA'], 'SubBacia.kmz', '2018 ou anterior — Plano Municipal de Saneamento'),
}
HEADERS={'User-Agent':'Feira-Integrada-Turma-307/3.0 (uso escolar; consulta de dados abertos)',
         'Accept':'application/json, application/xml, */*'}

def read_url(url):
    req=urllib.request.Request(url,headers=HEADERS)
    with urllib.request.urlopen(req,timeout=50) as response:return response.read()

def url_query(base,**params):
    return base+'?'+urllib.parse.urlencode(params)

def list_wfs(url):
    try:
        doc=ET.fromstring(read_url(url_query(url,service='WFS',version='1.0.0',request='GetCapabilities')))
        return [e.text.strip() for e in doc.iter() if e.tag.split('}')[-1]=='Name' and e.text and ':' in e.text]
    except Exception as err:
        print('Aviso: catálogo WFS não responde:',type(err).__name__,str(err)[:140])
        return []

def xy(lon,lat):
    lon=float(lon);lat=float(lat)
    if not (-180<=lon<=180 and -85<=lat<=85):raise ValueError('Não é coordenada geográfica')
    return [round((lon+180)/360*1e7),round((1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*1e7)]

def simplify(ring,tol=4):
    if len(ring)<5:return ring
    # Elimina pontos quase repetidos com limite de até 4 unidades Web Mercator normalizadas (~15 m)
    arr=[ring[0]]
    for p in ring[1:-1]:
        if abs(p[0]-arr[-1][0])+abs(p[1]-arr[-1][1])>=tol:arr.append(p)
    arr.append(ring[-1])
    return arr if len(arr)>=4 else ring

def feature_geom(g):
    typ=g.get('type');pts=g.get('coordinates') or []
    polys=[pts] if typ=='Polygon' else pts if typ=='MultiPolygon' else []
    result=[]
    for poly in polys:
        rings=[]
        for raw in poly:
            try:
                ring=simplify([xy(pt[0],pt[1]) for pt in raw])
                if len(ring)>=4:rings.append(ring)
            except (ValueError,TypeError,IndexError):continue
        if rings:result.append(rings)
    return result

def transform(features):
    results=[]
    for f in features:
        props=f.get('properties') or {}
        names=[str(v) for k,v in props.items() if v is not None and any(x in k.upper() for x in ('NOME','DESCRICAO','NM_'))]
        label=next((n.strip() for n in names if n.strip()),'Nome não identificado')
        for rings in feature_geom(f.get('geometry') or {}):
            xx=[pt[0] for ring in rings for pt in ring]
            yy=[pt[1] for ring in rings for pt in ring]
            bbox=[min(xx),min(yy),max(xx),max(yy)]
            if 3700000<bbox[0]<3860000 and 5400000<bbox[1]<5700000:
                results.append([bbox,rings,[label]])
    return results

def get_geojson(url,name):
    u=url_query(url,service='WFS',version='1.0.0',request='GetFeature',
                typeName=name,srsName='EPSG:4326',outputFormat='application/json',maxFeatures='15000')
    data=json.loads(read_url(u))
    if data.get('type')!='FeatureCollection':raise ValueError('Resposta não é GeoJSON de feições')
    a=transform(data.get('features',[]))
    if not a:raise ValueError('Nenhuma geometria compatível')
    return a,u,'PBH — IDE-BHGEO (WFS)','Ano de referência: conferir metadados da PBH'

def get_kmz(filename,year):
    url=KMZ_BASE+filename
    z=zipfile.ZipFile(io.BytesIO(read_url(url)))
    paths=[p for p in z.namelist() if p.lower().endswith('.kml')]
    if not paths:raise ValueError('KMZ sem KML')
    doc=ET.fromstring(z.read(paths[0]))
    features=[]
    for placemark in doc.iter():
        if placemark.tag.split('}')[-1]!='Placemark':continue
        name=next((c.text for c in placemark if c.tag.split('}')[-1]=='name' and c.text),'Nome não identificado')
        polygons=[]
        for pol in placemark.iter():
            if pol.tag.split('}')[-1]!='Polygon':continue
            rings=[]
            for lin in pol.iter():
                if lin.tag.split('}')[-1]!='LinearRing':continue
                for coords in lin:
                    if coords.tag.split('}')[-1]!='coordinates' or not coords.text:continue
                    pairs=[]
                    for part in coords.text.split():
                        try:
                            lon,lat=part.split(',')[:2]
                            pairs.append([float(lon),float(lat)])
                        except (ValueError,IndexError):continue
                    if len(pairs)>=4:rings.append(pairs)
            if rings:polygons.append(rings)
        if polygons:features.append({'properties':{'NOME':name},
                    'geometry':{'type':'MultiPolygon','coordinates':polygons}})
    out=transform(features)
    if not out:raise ValueError('Nenhuma geometria convertida')
    return out,url,'PBH — documento histórico KMZ',year

def main():
    sources={base:list_wfs(base) for base in SERVICES}
    manifest={}
    imported=0
    for key,(candidates,kmz,year) in TARGETS.items():
        output=None
        for base,layers in sources.items():
            if output:break
            for candidate in candidates:
                matches=[n for n in layers if n.rsplit(':',1)[-1].upper()==candidate]
                for layer in matches:
                    try:
                        output=get_geojson(base,layer)
                        break
                    except Exception as err:print('Falha na camada WFS:',key,layer,type(err).__name__)
                if output:break
        if not output:
            try:output=get_kmz(kmz,year)
            except Exception as err:print('Falha no KMZ:',key,type(err).__name__,str(err)[:110])
        if not output:
            manifest[key]={'status':'não obtido: fonte indisponível ou inválida'}
            print('Pendente:',key)
            continue
        features,url,source,reference=output
        record={'features':features,'source':source,'reference':reference,'url':url}
        path=OUT/(key+'.json')
        path.write_text(json.dumps(record,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
        manifest[key]={'feicoes':len(features),'source':source,'reference':reference,'url':url}
        imported+=1
        print('Importado:',key,len(features),'feições')
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # Arborização e renda não são inferidas de outros dados; aguardam indicadores verificados.
    if not imported:raise SystemExit('Nenhum serviço municipal respondeu com geometria válida')
if __name__=='__main__':main()
