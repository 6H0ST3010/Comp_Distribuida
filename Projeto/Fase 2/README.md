# Fase 2 - Arquitetura de 3 Camadas e API REST

## O Que Foi Feito

Dando continuidade à Fase 1, o objetivo desta fase foi uniformizar e abstrair a comunicação. Para tal, introduzimos uma nova camada intermédia: uma **API REST**.

## Escolhas de Implementação e Arquitetura

A arquitetura do sistema evoluiu de um modelo cliente/servidor para uma arquitetura de 3 camadas assente em três contentores Docker distintos:

1. **Backend (Web):** Continua a ser a porta de entrada para o utilizador, encarregue de renderizar as páginas. O *Backend* deixou de abrir Sockets diretamente e passou a utilizar pedidos HTTP padronizados (`GET`, `POST`, `PUT`, `DELETE`).
2. **API REST (Camada Intermédia):** Este novo contentor atua como ponte. A sua função é receber os pedidos HTTP originados no *Backend* e **traduzi-los** para mensagens por Sockets TCP (em formato JSON) que o *Data Service* consegue interpretar. 
3. **Data Service:** Continua responsável por aceder aos ficheiros físicos (`utilizadores.json` e `dados.json`). Agora apenas recebe tráfego oriundo do contentor da API REST, melhorando o isolamento da rede.

**Base de Dados JSON:**
Mantivemos a base de dados suportada pelos ficheiros `.json` nativos. Esta escolha contínua revelou-se eficaz na tradução de mensagens, visto que o JSON transita facilmente entre HTTP e Sockets. Para suportar a carga de pedidos traduzidos pela API REST, implementámos concorrência com *threads* no `data_server.py`.

## Pontos de Melhoria Identificados

- **Documentação da API (Swagger):** Não foi implementada nenhuma documentação formal para a API REST. A utilização do **Swagger** (ou OpenAPI) seria uma mais-valia evidente, pois facilitaria a interatividade, testes e perceção imediata dos *endpoints* construídos.
- **Acessibilidade do Data Service:** O nosso sistema de dados baseia-se em *sockets* costumizados e num ficheiro JSON em vez de um SGBD convencional, o que vai originar algumas dificuldades quando terceiros tentarem aceder/usar a nossa base de dados.

## Como Funciona e Utilização

1. Navegue até a esta pasta: `cd "Projeto/Fase 2"`
2. No terminal, inicie a orquestração dos 3 contentores:
   ```bash
   docker compose up --build
   ```
3. Aceda ao interface em **http://localhost:8080**.
4. Ao clicar na página das Lojas, o *Backend* faz um pedido HTTP à *API REST*, que abre um Socket com o *Data Service* para consultar a lista guardada no `.json`, devolvendo a resposta até ao utilizador.

## Utilização de IA
No desenvolvimento desta fase foi utilizado o chat para ajudar na realização do mesmo, resolver alguns problemas e na documentação do relatório.
Alguns exemplos de prompts utilizados foram:
- "Preciso de converter uma API HTTP Flask num intermediário que envia os dados para um servidor backend via Sockets TCP em Python. Como posso estruturar o ciclo de vida da mensagem (request/response) usando JSON sobre Sockets?"
