# Relatório do Projeto - Fase 2

## Introdução

O objetivo desta Fase 2 consiste na evolução e adaptação de uma aplicação Web preexistente para um ambiente distribuído assente em contentores (utilizando Docker ou Podman). Para tal, a aplicação foi segmentada logicamente, separando a interface do utilizador e a lógica de negócio do sistema de persistência de dados.
Através desta implementação, foram consolidados conceitos práticos fundamentais de computação distribuída, tais como:
- Comunicação entre processos: Através de redes de computadores com recurso a sockets;
- Modelo Cliente/Servidor: Descomposição de responsabilidades em múltiplos níveis de atendimento;
- APIs REST: Intermediação padronizada de serviços via protocolo HTTP.

## Arquitetura do Sistema
O sistema foi desenhado seguindo uma arquitetura de 3 camadas:
- Backend: É o único ponto de contacto exposto ao cliente. É responsável pela renderização das páginas HTML através de templates, validação de dados de formulários e processamento de ficheiros multimédia.
- API REST: Suportada por um contentor isolado, esta camada atua como uma ponte entre as duas outras camadas. Traduz os pedidos HTTP para pedidos socket.
- Data_service: Consiste num servidor que comunica através de Sockets. Esta componente manipula diretamente os ficheiros físicos em formato JSON (utilizadores.json e dados.json), garantindo a escrita e leitura síncrona da informação.

Para realizar os pedidos HTTP ao API REST, foram desenvolvidas quatro funções que utilizam a biblioteca requests: api_get, api_post, api_put e api_delete. Cada uma destas funções faz um pedido HTTP para o API REST, api_get('/users').
O API REST traduz esse HTTP para pedido socket da seguinte maneira:
- Cria um socket e conecta-se ao host data-service no porto.
- Serializa o dicionário (payload) em formato string JSON codificada em utf-8 e envia-o.
- Fecha a extremidade de escrita para sinalizar ao servidor que o pedido terminou.
- Recolhe a resposta em blocos de 4096 bytes, reconstrói o texto e efetua o parse do JSON de retorno.
Os métodos das rotas da API (/api/users e /api/lojas) limitam-se a receber os pedidos HTTP da camada Web, encapsular as intenções num dicionário contendo uma chave "action" (ex: {"action": "get_all_users"} e invocar a função socket_request. O retorno é devolvido ao Backend Web acompanhado pelos respetivos códigos de estado HTTP.
Por fim no data_server é estabelecida a conexão e é instanciada uma nova e independente thread de execução, garantindo o processamento concorrente de múltiplos pedidos:
No método handle_client(conn), o servidor lê os dados enviados pelo cliente até que a transmissão termine. O payload JSON recebido é descodificado e a chave action é avaliada num bloco condicional. Consoante a ação especificada, o servidor executa operações.
