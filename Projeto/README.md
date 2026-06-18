# Projeto de Computação Distribuída

**Curso:** LEIC
**Grupo:**
- Rodrigo Amaral (15318)
- Martim Ceirao (15316)
- Miguel Lopes (15344)

## Visão Geral

Este diretório contém o projeto desenvolvido no âmbito da unidade curricular de Computação Distribuída. 
O ponto de partida para este trabalho foi uma aplicação Web de uma loja online, desenvolvida previamente noutra unidade curricular. O foco deste projeto foi evoluir essa arquitetura monolítica para um sistema distribuído e moderno.

Ao longo de três fases, transformámos a loja num ecossistema baseado em microsserviços, contentorizado (utilizando Docker) e integrado com sensores da Internet das Coisas (IoT).

## Evolução da Arquitetura

O trabalho foi dividido em 3 fases incrementais (com detalhes mais específicos nos READMEs de cada pasta):

1. **[Fase 1](./Fase%201/README.md):** 
   - Contentorização do sistema.
   - Separação da lógica em duas camadas: o *Backend* (servidor Web) e o *Data Service* (persistência de dados).
   - Utilização de sockets TCP e mensagens em formato JSON para a comunicação síncrona entre estas duas camadas. 

2. **[Fase 2](./Fase%202/README.md):**
   - Introdução de uma camada intermédia, estabelecendo uma arquitetura de 3 camadas.
   - Criação de uma **API REST** que serve de ponte entre o *Backend* e o *Data Service*. Isto uniformizou o acesso aos dados e abstraiu o protocolo de baixo nível (sockets).

3. **[Fase 3](./Fase%203/README.md):**
   - Integração com dispositivos IoT.
   - Adição de um *Dashboard* à loja para monitorização em tempo real.
   - Comunicação via MQTT (Publish/Subscribe) para ler dados de uma tomada inteligente.
   - Comunicação via REST para consumir dados meteorológicos.
   - Resolução de problemas de CORS utilizando a nossa própria API REST como *Proxy* reverso.

## Limitações e Pontos a Melhorar (Trabalho Futuro)

Durante o desenvolvimento, identificámos alguns pontos que limitam a usabilidade e expansão do sistema por terceiros:
- **Base de Dados proprietária (JSON):** Como implementámos o *Data Service* através da leitura/escrita direta em ficheiros `.json` usando sockets customizados, o nosso sistema de base de dados não é facilmente acessível nem integrável com ferramentas ou equipas externas que tentem interagir com os nossos dados de forma standard. A transição para um SGBD real resolveria isto.
- **Falta de Documentação da API:** A *API REST* criada na Fase 2 carece de documentação interativa (como o **Swagger**). A adoção do Swagger facilitaria imenso a visualização e teste dos *endpoints* da API.

## Como Executar e Utilizar o Projeto

Para correr a versão final do projeto (recomendamos executar a Fase 3):

1. Certifique-se de que tem o **Docker** e o **Docker Compose** instalados na sua máquina.
2. Abra o terminal e navegue até à diretoria da fase desejada:
   ```bash
   cd "Fase 3"
   ```
3. Execute o comando para construir e iniciar os contentores:
   ```bash
   docker compose up --build
   ```
4. O sistema irá iniciar os microsserviços necessários.
5. Abra o seu browser e aceda à aplicação em: **http://localhost:8080**
6. A partir daí, poderá navegar na loja, fazer login e aceder ao Dashboard IoT. Login para testar: username - teste, password - 123.
