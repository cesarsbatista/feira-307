# Raízes da Desigualdade — Missão Justiça Climática V2

**Escola Estadual Governador Milton Campos · Turma 307 · Feira Integrada de Ciência, Tecnologia, Cultura e Inovação 2026**

## Abrir a aplicação

**https://cesarsbatista.github.io/feira-307/** (GitHub Pages deve estar habilitado na branch `main`, pasta `/(root)`).

## O que foi implementado na V2

- **Mapa:** oito camadas cartográficas, pesquisa de rua (online), consulta de atributos e transparência das camadas.
- **Comparar:** seleção de dois pontos A e B e tabela com os indicadores disponíveis nas respectivas posições.
- **Soluções:** jardim de chuva, microárea de sombra e corredor ecológico, laboratório didático e ficha de intervenção para imprimir ou exportar.
- **Apresentar:** cinco etapas relacionadas à pergunta, metodologia e proposta da pesquisa, com ativação contextual das camadas.
- **Pesquisa:** problema, hipótese, etapas concluídas/planejadas, ODS 10, 11, 13 e 15, fontes e limitações de cada camada.

## Limites fundamentais

O comparador é **pontual e exploratório**: não calcula médias, correlações, índices ou rankings de bairros. O pacote cartográfico recebido **não contém camadas específicas de arborização de vias, indicadores sociais ou limites de bairros compatíveis**. Esses dados serão necessários para validar comparações territoriais.

O indicador **EXP_ONDA** não mede temperatura em graus Celsius nem representa, sozinho, um mapa medido de ilhas de calor. Uma posição fora de um polígono de risco cadastrado não comprova ausência de risco. Os metadados de produção das bases precisam ser verificados com as fontes oficiais. Não use a ferramenta como laudo ou alerta em tempo real.

## Estrutura técnica

- `index.html`: página e funcionalidades da V2.
- `dados/parte-01.txt` a `dados/parte-15.txt`: dados geográficos extraídos das camadas encaminhadas no pacote QGIS.
- `.nojekyll`: configuração de publicação estática.

A aplicação usa arquivos locais no próprio repositório e não depende de um servidor de mapas. Pesquisa de ruas e mapa-base OpenStreetMap necessitam de internet. Para uso offline sem servidor web, utilize o HTML único fornecido como backup na conversa.

## Fontes para conferir metadados

- [BHGeo — Acervo Cartográfico](https://prefeitura.pbh.gov.br/bhgeo/acervo-cartografico)
- [Plano Municipal de Arborização Urbana](https://prefeitura.pbh.gov.br/meio-ambiente/plano-municipal-de-arborizacao-urbana)
- [Plano Local de Ação Climática](https://prefeitura.pbh.gov.br/meio-ambiente/plano-local-de-acao-climatica-de-belo-horizonte)
- [IBGE — Censo 2022: entorno dos domicílios](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/tipologias-do-territorio/24702-caracteristicas-urbanisticas-do-entorno-dos-domicilios.html)

O projeto é um produto educativo, fundamentado no texto escrito da turma, e não se confunde com uma pesquisa de campo concluída.
