# Fase 1 - Contentorização e Modelo Cliente/Servidor

## O Que Foi Feito

Nesta primeira fase, iniciámos a transição do sistema para uma arquitetura distribuída. O objetivo principal foi separar a componente Web (interface e lógica de servidor) da componente de persistência de dados.

## Escolhas de Implementação e Arquitetura

Dividimos o sistema em dois servidores que correm em contentores Docker separados:
1. **Backend (Aplicação Web):** O contentor que serve as páginas HTML e gere a interface com o utilizador. Este é o único contentor que está exposto e acessível a partir do host.
2. **Data Service (Persistência):** Um contentor isolado na sua rede, com a responsabilidade única de gerir a leitura e escrita na base de dados (`dados.json` e `utilizadores.json`).

**Comunicação via Sockets e JSON:**
Decidimos que a comunicação entre o *Backend* e o *Data Service* seria feita de forma nativa através de **sockets TCP**. Para garantir que os dados transitam bem estruturados e são fáceis de processar, optámos por utilizar o formato **JSON** em todas as mensagens. 
- **O Cliente (Backend):** Ao receber um pedido do utilizador (por exemplo, pedir informações de um perfil), abre uma ligação socket, cria um payload JSON com a ação correspondente (ex: `{"action": "get_user", "username": "admin"}`), envia-o para o *Data Service* e aguarda resposta.
- **O Servidor (Data Service):** Escuta no porto configurado, processa a string JSON que recebe, manipula os ficheiros `.json` guardados no volume e devolve a resposta ao *Backend*.

Optámos por manter a base de dados em ficheiros `.json` porque ofereciam uma leitura simples e adaptavam-se bem à estrutura de chaves e valores que necessitávamos nesta fase.

## Como Funciona e Utilização

1. Navegue até a esta pasta: `cd "Projeto/Fase 1"`
2. No terminal, execute o comando:
   ```bash
   docker compose up --build
   ```
3. Aceda à loja no browser no endereço **http://localhost:8080**.
4. Interaja com o site normalmente. Por baixo dos panos, o *Backend* irá comunicar com o *Data Service* via TCP/Sockets sempre que for preciso aceder ou alterar informação.

## Utilização de IA
No desenvolvimento desta fase foi utilizado o chat para ajudar na realização do mesmo, resolver alguns problemas e na documentação do relatório.
Alguns exemplos de prompts utilizados foram:
- "Escreve um script simples em Python que utilize a biblioteca socket para se ligar a um servidor local . O script deve enviar um payload JSON com {"action": "get_all_users"}"
