# Relatório do Projeto - Fase 3

## Introdução

Este relatório documenta o desenvolvimento e a implementação da Fase 3 do Trabalho Prático, cujo foco central reside na extensão de uma plataforma Web preexistente através da integração de ecossistemas da Internet das Coisas (IoT).

Os objetivos principais desta fase consistem em:
- Integração Multitópico de Dispositivos IoT: Recolha de dados em tempo real provenientes de sensores ambientais e de consumo energético.
- Convergência de Protocolos: Coexistência e manipulação prática de modelos de comunicação baseados no paradigma Request-Response (via API REST) e no paradigma Publish-Subscribe (via protocolo MQTT).
- Mitigação de Restrições de Segurança (CORS): Implementação de um mecanismo de Proxy inverso no servidor para contornar políticas de Cross-Origin Resource Sharing.

## Arquitetura do Sistema

Modelo Cliente/Servidor (REST): Utilizado para o consumo de dados meteorológicos. O cliente efetua pedidos HTTP ao servidor, que atua como intermediário no consumo de um Web Service externo focado em dados geográficos e climatéricos.
Modelo Publish/Subscribe (MQTT): Utilizado para a monitorização de consumo elétrico de uma tomada inteligente. Oservidor lia-se ao Broker e recebe os dados do sensor em tempo real.

Na componente REST API foram criadas 2 rotas para atuar como pontes de comunicação ambas utilizando HTTPBasicAuth.
- /api/weather/values: Obtém variáveis ambientais como temperatura e humidade.
- /api/weather/position: Consome os dados geográficos da estação meteorológica, expondo a latitude e longitude do dispositivo remoto.

A componente MQTT foi dividida em 3 partes:
- iniciar_mqtt: Configura o cliente MQTT e inicia o ciclo de escuta permanente;
- on_connect: Assim que a ligação ao Broker público (cjsg.ddns.net:1883) é estabelecida com sucesso, este método é ativado e subscreve imediatamente o tópico /power para começar a escutar o dispositivo;
- on_message: Sempre que a tomada inteligente envia novas leituras, este método intercepta o pacote de dados e é descodificado para texto, convertido de formato JSON.
