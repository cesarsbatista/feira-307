# Missão Justiça Climática — Turma 307

**Atlas Ambiental Interativo de Belo Horizonte**

**Escola Estadual Governador Milton Campos** · **Turma 307** · **Feira Integrada 2026**

## Acesso

Após habilitar o GitHub Pages: **https://cesarsbatista.github.io/feira-307/**

## Conteúdo

WebGIS educacional com oito camadas temáticas, incluindo áreas de risco de inundação e escorregamento, exposição a ondas de calor, alagamento, cursos d'água, conexões verdes e permeabilidade. Permite ligar e desligar camadas, ajustar transparência, clicar para consultar atributos, pesquisar ruas com internet e seguir percursos temáticos.

## Estrutura

- `index.html`: interface, cartografia e lógica de visualização.
- `dados/parte-01.txt` a `dados/parte-15.txt`: dados geográficos, divididos em blocos menores para publicação via GitHub.
- `.nojekyll`: garante publicação direta dos arquivos estáticos pelo GitHub Pages.

Os 15 arquivos de dados precisam estar disponíveis junto com o `index.html`. **Não use apenas o HTML do GitHub para funcionar offline**. Para uso sem conexão, mantenha a versão local completa em HTML previamente entregue.

## Habilitar GitHub Pages

No repositório, acesse **Settings → Pages → Build and deployment**. Escolha **Deploy from a branch**, selecione **main**, **/(root)** e clique em **Save**.

O projeto é uma cópia dos dados do QGIS, não uma atualização automática dos arquivos .qgz. A pesquisa de ruas e o mapa-base utilizam serviços externos; exigem internet. Os dados não representam alertas de enchentes em tempo real nem laudos de imóveis. Confirme autoria e atualização dos dados com suas fontes originais.
