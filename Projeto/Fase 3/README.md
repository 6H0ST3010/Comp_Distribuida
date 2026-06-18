# Fase 3 - Integração IoT e Dashboard

## O Que Foi Feito

Nesta fase final, expandimos as funcionalidades da loja online. Tendo como fundação a arquitetura distribuída criada nas fases anteriores, implementámos a recolha de dados de dispositivos e sensores (IoT), culminando na criação de um novo *Dashboard* para visualização em tempo real.

## Escolhas de Implementação e Arquitetura

Para integrar estes sensores, convergimos dois modelos de comunicação na nossa infraestrutura:

1. **Protocolo MQTT (Publish/Subscribe) para Consumo Energético:**
   - Para monitorizar uma **tomada inteligente**, optámos pelo MQTT. Este protocolo é leve e reativo. O nosso servidor liga-se a um Broker público ao arrancar e subscreve o tópico `/power`. Através da função `on_message`, a plataforma atualiza-se imediatamente quando a tomada reporta um evento.

2. **API REST (Request/Response) para Sensores Ambientais:**
   - Para aceder aos dados climatéricos (temperatura, humidade e geolocalização) de uma estação meteorológica, consumimos um serviço remoto externo via HTTP utilizando REST e autenticação `HTTPBasicAuth`.

3. **Resolução de Problemas de CORS (Proxy Reverso):**
   - Ao integrar os sensores REST, deparámo-nos com bloqueios de segurança do *browser* (CORS).
   - **A nossa solução:** Em vez de fazer o *Javascript* da aplicação tentar aceder diretamente ao Web Service externo, utilizámos a nossa *API REST* interna para atuar como **Proxy**. Criámos as rotas `/api/weather/values` e `/api/weather/position`. O *Backend* faz o pedido a estas rotas internas com segurança, o servidor contacta a fonte original na web, recolhe os dados e serve-os ao *frontend*, contornando o CORS.

## Como Funciona e Utilização

1. No terminal, navegue para: `cd "Projeto/Fase 3"`
2. Levante a arquitetura final com:
   ```bash
   docker compose up --build
   ```
3. Aceda à aplicação via **http://localhost:8080**.
4. Dirija-se à área do novo **Dashboard IoT**.
5. Neste ecrã verá os dados a serem atualizados: as métricas ambientais via pedidos REST em *background*, e o consumo de energia atualizado imediatamente pelas publicações MQTT.
