# Relatório do Projeto - Fase 1

## Introdução e Objetivos

O presente relatório surge no âmbito da Fase 1 da unidade curricular de Computação Distribuída. O trabalho prático consiste na evolução e adaptação de uma aplicação Web previamente desenvolvida na unidade curricular de Programação Web para um ambiente moderno e isolado assente em microsserviços e contentores.
Os objetivos principais desta fase centram-se na adoção do modelo arquitetural cliente/servidor e na utilização prática de tecnologias de contentorização.

## Arquitetura do Sistema e Modelo Cliente/Servidor

O sistema foi redesenhado seguindo uma arquitetura clássica de duas camadas, em que cada camada é executada num servidor logicamente distinto e isolado:
- Backend: Contentor Flask
- Data_service: Contentor de dados

A comunicação entre as duas camadas baseia-se na implementacção de sockets e para garantir a estruturação dos dados, todas as mensagens de pedido e resposta utilizam o formato JSON.
As mensagens seguem a seguinte estrutura:
O cliente (Servidor Web) envia uma propriedade action que determina a operação a executar (get_user), acompanhada opcionalmente por dados adicionais (username).

A aplicação Web (Server.py) atua como intermediária. Quando recebe um pedido HTTP através dos seus endpoints, invoca a função auxiliar send_socket_request(), que abre uma ligação TCP para o data_server, envia o payload JSON correspondente, aguarda a resposta e fecha a ligação.

