# Referência territorial — bairros oficiais de Belo Horizonte

Base enviada pelo usuário em 18/11/2026: `BELO HORIZONTE_BAIRRO_OFICIAL.shp`, com arquivos auxiliares DBF, SHX e PRJ.

- Sistema de coordenadas: **SIRGAS 2000 / UTM zona 23S (EPSG:31983)**.
- **323 feições**; **303 nomes distintos**, pois há bairros com geometrias em mais de uma feição.
- Campo de identificação: **NOME**. Classificação territorial: **TIPO**.
- Composição do campo TIPO: Bairro (170), Vila (91), Conjunto Habitacional (26), Seção Urbana (14), Parque (9), Seção Suburbana (6), Ex Colônia (5), Zona Urbana (1) e Jardim (1).
- O nome **Serra não consta** nesse shapefile. **Serra Verde** e **Serrano** estão presentes e são entidades distintas. Não criar polígono artificial para Serra.
- Atenção: `dados-externos/bairros.json` já contém 303 nomes distintos, correspondentes em quantidade à fonte enviada. Não assumir que isso comprova identidade geométrica; para substituir a geometria, converter o shapefile e conferir atributos e topologia.

## Critérios de uso

1. Priorizar o campo `NOME` para pesquisa, seleção e comparação.
2. Ao informar que a feição está ausente, distinguir ausência de registro da falta de risco.
3. Preservar todas as partes de geometrias multipartes e reprojetar EPSG:31983 para WGS84 antes de converter a coordenadas normalizadas utilizadas no WebGIS.
4. Não substituir o bairro Serra por Serra Verde ou Serrano nem apresentar um resultado alternativo como correspondência exata.
5. Preservar os dados territoriais enquanto não houver validação de uma exportação completa do shapefile.

O shapefile original foi fornecido na conversa e não está incluído neste repositório; este documento registra seus metadados auditados.
