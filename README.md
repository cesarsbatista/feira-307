# Raízes da Desigualdade — Missão Justiça Climática V6

**Escola Estadual Governador Milton Campos (Estadual Central)** · **Turma 307** · **Feira Integrada 2026**

## Acessar

- [Abrir o mapa interativo](https://cesarsbatista.github.io/feira-307/)
- [Código e histórico](https://github.com/cesarsbatista/feira-307)

## Seleção de ruas completas — base oficial PBH

- Fonte preferencial: cadastro **TRECHO_LOGRADOURO** da PBH/Prodabel, agrupado por **ID_LOGRADOURO** (todos os trechos pertencentes à via), com zoom para a extensão recuperada.
- A aplicação tenta primeiro os arquivos locais em `dados-externos/logradouros/`. Enquanto não estiverem disponíveis, utiliza o serviço WFS municipal e, em último caso, o OpenStreetMap.
- Importador: `scripts/importar_logradouros.py`; workflow GitHub Actions: `.github/workflows/importar-logradouros.yml`. Executa ao publicar o workflow/script ou manualmente pela opção **Run workflow**.
- A importação só publica após verificar quantidade mínima de feições e agrupamentos; em caso de erro, não deve substituir a base local por uma exportação incompleta.
- **Limitação:** a importação e as consultas WFS dependem da disponibilidade e permissões do serviço municipal. A implementação em código não comprova que o arquivo local foi efetivamente gerado. Confirmar em `dados-externos/logradouros/index.json` e testar o resultado no mapa.

## Atualização — classificação qualitativa dos indicadores climáticos

- Calor, inundação (indicador SBN) e alagamento (indicador SBN) passam a utilizar **Baixo, Médio, Alto e Muito alto** em vez de valores numéricos, nas consultas, comparação e legenda.
- As classes são relativas aos quartis de cada indicador nos valores válidos da base fornecida e **não são classificações oficiais de risco**.
- Na comparação territorial de bairros, informa-se a **maior classe encontrada em qualquer polígono que intersecte o bairro**, sem afirmar que toda sua extensão apresenta essa condição.
- O cadastro vetorial de **áreas de risco de inundação** continua separado do indicador SBN de inundação, mantendo a regra de interseção espacial para cada bairro.

## Atualização — comparação territorial de bairros

- Ao escolher um bairro pela busca ou pelo seletor, o sistema abre **Comparar** e preenche automaticamente A, depois B (ou substitui B caso ambos já estejam ocupados).
- Indicadores binários de inundação, escorregamento e conexão verde consideram **interseção dos polígonos cadastrados com qualquer parte do perímetro do bairro**.
- Indicadores numéricos de calor, alagamento, inundação e permeabilidade exibem a **faixa mínima–máxima dos polígonos que intersectam o bairro**, sem média ou ponderação por área.
- Dados sociais continuam associados ao bairro quando a base de referência está disponível. Arborização setorial não é convertida em uma média fictícia de bairro.
- Comparações pontuais permanecem disponíveis para consultas a locais específicos.

## V6 — alterações implementadas

- Ao trocar entre as abas **Mapa, Comparar, Soluções, Apresentar e Pesquisa**, as seleções temporárias são limpas: bairros destacados, pontos pesquisados, marcadores de comparação A/B, sugestões e janelas informativas. A troca de abas preserva o enquadramento atual, exceto na aba Apresentar.
- O título lateral passa a ser **Raízes da desigualdade** (sem ponto final).
- Mapa de ruas alterado para **CARTO Positron**, com cartografia suave e menos elementos visuais que o mapa convencional. Algumas etiquetas de interesse ainda podem aparecer; satélite e dados temáticos permanecem disponíveis. Créditos a OpenStreetMap e CARTO.

## V5 — alterações implementadas

- Modo **Apresentar** oculta a pesquisa e enquadra o limite completo de Belo Horizonte (utilizando a geometria municipal disponível; enquadramento aproximado enquanto carrega).
- Ao entrar em **Apresentar**, são retirados os destaques anteriores de bairros, marcadores, pontos de comparação e janelas de informação. As camadas temáticas do roteiro continuam ativas conforme a etapa da apresentação.
- Barra de pesquisa mais estreita e mais próxima das bordas superiores e laterais, com adaptação para telas pequenas.
- Sugestões locais de bairros, cursos d'água e conexões verdes durante a digitação; pesquisas de endereço na internet permanecem disponíveis ao clicar em **Buscar**.
- O painel da apresentação mostra somente a pergunta, sem o prefixo “Pergunta ao público”.

## V4 — alterações implementadas

- Cabeçalho e painel esquerdo mais estreitos, sem o subtítulo redundante “Raízes da Desigualdade · Belo Horizonte” nem o letreiro duplicado da feira no painel.
- Pop-up de seleção A/B deslocado para longe da busca; barra de pesquisa discretamente menor.
- A busca localiza um ponto e posiciona o marcador **sem abrir automaticamente o quadro “Leitura do território”**; o quadro abre ao clicar no marcador ou diretamente no mapa.
- Legenda das camadas recolhida inicialmente, aberta apenas pelo novo ícone da barra lateral.
- Comparação A/B sem coordenadas exibidas.
- Seleção de um bairro pela lista/pesquisa, com contorno e preenchimento semitransparente, zoom, nome e botão para limpar.
- Limite de Belo Horizonte com perímetro e sombreamento externo, quando a geometria oficial importada estiver disponível, além de botão de enquadramento.
- Perfil socioambiental por bairro, com população, domicílios e densidade do Censo 2022 **quando a tabela oficial da Prefeitura estiver carregada**; mapa temático de densidade por bairro, sem interpolar valores.
- No comparador, **valores climáticos referentes ao ponto e demografia referente ao bairro são indicados com seus diferentes recortes**.

## Dados e fontes

Os dados ambientais iniciais vêm dos oito conjuntos cartográficos encaminhados pela turma e continuam no diretório `dados/`. Bairros, regionais, bacias e sub-bacias foram importados de dados oficiais e documentos públicos da Prefeitura de Belo Horizonte para `dados-externos/`.

O script `scripts/importar_v4.py` acrescenta a **Malha Municipal do IBGE (código 3106200)** e a tabela oficial da **PBH/Prodabel “População e Domicílio por Bairro 2022”**, gerando `dados-externos/municipio.json` e `dados-externos/perfil_bairros.json`. O workflow pode ser executado manualmente em Actions ou por mudanças nos scripts.

- [PBH — População e Domicílio por Bairro 2022](https://dados.pbh.gov.br/dataset/populacao-e-domicilio-por-bairro-2021/resource/4f51b598-374a-482b-a7b3-a7b4ce1beda8)
- [IBGE — Malhas municipais](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/15774-malhas.html)
- [IBGE — Características Urbanísticas do Entorno dos Domicílios](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/tipologias-do-territorio/24702-caracteristicas-urbanisticas-do-entorno-dos-domicilios.html)
- [BHGeo — Acervo Cartográfico](https://prefeitura.pbh.gov.br/bhgeo/acervo-cartografico)

## Limitações importantes

A **arborização do Censo 2022 ainda não foi incorporada**, porque a base vetorial por setor censitário e o seu indicador percentual precisam ser processados e validados antes de fazer uma representação fiel. O inventário individual de árvores não está publicamente disponível em formato completo confirmado. Da mesma forma, **renda, idade e cor/raça por bairro ainda não estão incorporadas**. A aplicação sinaliza essas indisponibilidades, em vez de inventar números.

A população, os domicílios e a densidade referem-se ao **bairro como um todo**; a interseção com áreas de inundação, escorregamento, calor e permeabilidade é uma **consulta pontual**, não uma média por bairro.

O mapa é **educativo, não um sistema oficial de previsão, alerta de enchentes, laudo de risco ou aferição instantânea de temperatura**. A ausência de risco na geometria consultada não comprova ausência de risco real.

## Operação offline

O código inicial mantém as camadas originais em arquivos estáticos, mas mapas-base e pesquisa geocodificada dependem da internet. Para utilização offline, gere a versão incorporada dos arquivos com `scripts/gerar_offline.py` após a importação das camadas oficiais.
