# Raízes da Desigualdade — Missão Justiça Climática V5

**Escola Estadual Governador Milton Campos (Estadual Central)** · **Turma 307** · **Feira Integrada 2026**

## Acessar

- [Abrir o mapa interativo](https://cesarsbatista.github.io/feira-307/)
- [Código e histórico](https://github.com/cesarsbatista/feira-307)

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
