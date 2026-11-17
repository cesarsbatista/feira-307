#!/usr/bin/env python3
"""Importação V4: limite municipal oficial IBGE e população por bairro PBH/Censo 2022."""
import csv,io,json,urllib.parse
from importar_bhgeo import OUT,get,normalize

MALHA='https://servicodados.ibge.gov.br/api/v3/malhas/municipios/3106200'
CSV='https://ckan.pbh.gov.br/dataset/a6bfc464-a88b-4b50-a653-05f7975d5208/resource/4f51b598-374a-482b-a7b3-a7b4ce1beda8/download/20250801_populacao_domicilio_bairro_2022.csv'

def municipio():
    for quality in ['maxima','intermediaria']:
        url=MALHA+'?'+urllib.parse.urlencode({'formato':'application/vnd.geo+json','qualidade':quality})
        try:
            data=json.loads(get(url,40))
            if data.get('type')=='FeatureCollection':raw=data['features']
            elif data.get('type')=='Feature':raw=[data]
            elif data.get('type') in ('Polygon','MultiPolygon'):raw=[{'geometry':data,'properties':{}}]
            else:raise ValueError('API não retornou GeoJSON')
            raw=[{'type':'Feature','geometry':f.get('geometry'),'properties':dict(f.get('properties') or {},NOME='Belo Horizonte')} for f in raw]
            features,_=normalize(raw)
            if not features or len(features)>25:raise ValueError('Malha municipal inesperada')
            result={'features':features,'source':'IBGE — API de Malhas Municipais, código 3106200','reference':'Malha oficial do município, versão do serviço IBGE','url':url,'count':len(features)}
            (OUT/'municipio.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n','utf-8')
            print('OK município IBGE',len(features))
            return {k:result[k] for k in ['source','reference','url','count']}
        except Exception as e:print('Aviso: município IBGE',str(e)[:240])
    return {'status':'malha municipal não obtida'}

def numeric(v):
    st=str(v or '').strip().replace(' ','')
    if ',' in st:st=st.replace('.','').replace(',','.')
    try:return float(st)
    except ValueError:return None

def populacao():
    raw=get(CSV,65)
    txt=None
    for codec in ['utf-8-sig','cp1252','latin-1']:
        try:txt=raw.decode(codec);break
        except UnicodeDecodeError:pass
    if txt is None:raise ValueError('CSV sem codificação reconhecida')
    line=txt.splitlines()[0]
    rows=csv.DictReader(io.StringIO(txt),delimiter=';' if line.count(';')>=line.count(',') else ',')
    bairros=[]
    for row in rows:
        obj={str(k or '').strip().upper():str(v or '').strip() for k,v in row.items() if k}
        name=obj.get('BAIRRO','')
        pop=numeric(obj.get('POPULACAO'))
        dom=numeric(obj.get('DOMICILIOS'))
        density=numeric(obj.get('DENSIDADE_DEMOGRAFICA'))
        area=numeric(obj.get('AREA_KM'))
        if not name or pop is None or dom is None or pop<0 or dom<0:continue
        if density is None and area and area>0:density=pop/area
        if density is not None and not 0<=density<1_000_000:density=None
        bairros.append({'nome':name,'populacao':int(pop),'domicilios':int(dom),'densidade':round(density,2) if density is not None else None,'area_km2':area})
    if len(bairros)<50:raise ValueError('A tabela não contém 50 bairros válidos')
    result={'source':'Prefeitura de Belo Horizonte / Prodabel — Censo IBGE 2022','reference':'População e Domicílio por Bairro 2022; publicação 07/08/2025','url':CSV,'count':len(bairros),'bairros':bairros,'method':'Recorte por bairro já divulgado pela PBH; sem interpolação ou inferência.'}
    (OUT/'perfil_bairros.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n','utf-8')
    print('OK população/domicílios',len(bairros))
    return {k:result[k] for k in ['source','reference','url','count']}

if __name__=='__main__':
    OUT.mkdir(exist_ok=True,parents=True)
    report={}
    try:report['municipio']=municipio()
    except Exception as e:report['municipio']={'status':str(e)}
    try:report['perfil_bairros']=populacao()
    except Exception as e:report['perfil_bairros']={'status':str(e)}
    p=OUT/'manifest.json'
    try:manifest=json.loads(p.read_text('utf-8'))
    except Exception:manifest={}
    manifest.update(report)
    p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
