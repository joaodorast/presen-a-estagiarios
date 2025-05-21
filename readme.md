# SEICE - Sistema de Estágio e Controle de Estagiários

## Sobre o Projeto

SEICE (Sistema de Estágio e Controle de Estagiários) é uma aplicação web completa para gerenciar estagiários e seus registros de presença. O sistema facilita o controle de horários, frequência e relatórios, tornando mais eficiente a administração de programas de estágio.

## Funcionalidades

- **Gerenciamento de Estagiários**
  - Cadastro, atualização e exclusão de dados de estagiários
  - Controle de status (ativo/inativo)
  - Armazenamento de informações de contato

- **Registro de Presenças**
  - Registro de entrada e saída
  - Cálculo automático de horas trabalhadas
  - Histórico completo de presenças
  - Observações para cada registro

- **Relatórios e Estatísticas**
  - Relatórios de frequência
  - Estatísticas por estagiário
  - Totais de horas trabalhadas
  - Médias diárias

- **Configurações do Sistema**
  - Horários padrão de entrada e saída
  - Tolerância para atrasos
  - Controle de feriados

## Tecnologias Utilizadas

- **Backend**: Go (Golang)
- **Banco de Dados**: MySQL
- **API**: RESTful com Gorilla Mux
- **Frontend**: HTML, CSS e JavaScript (servido pelo backend)

## Requisitos

- Go 1.16 ou superior
- MySQL 5.7 ou superior
- Sistema operacional compatível (Windows, macOS, Linux)

## Instalação e Configuração

### 1. Preparando o Ambiente

Primeiro, certifique-se de ter Go e MySQL instalados em seu sistema.

#### Instalando Go (se necessário)

Faça o download e instale Go a partir do [site oficial](https://golang.org/dl/).

#### Instalando MySQL (se necessário)

Faça o download e instale MySQL a partir do [site oficial](https://dev.mysql.com/downloads/mysql/).

### 2. Clonando o Repositório

```bash
(https://github.com/joaodorast/presen-a-estagiarios.git)
cd seice
```

### 3. Configurando o Banco de Dados

O sistema está configurado para se conectar ao MySQL usando as seguintes configurações padrão:

- **Usuário**: root
- **Senha**: (vazia)
- **Host**: localhost
- **Porta**: 3306
- **Banco de Dados**: seice

Se você precisar alterar essas configurações, há duas opções:

#### Opção 1: Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```
DB_USER=seu_usuario
DB_PASS=sua_senha
DB_HOST=seu_host
DB_PORT=sua_porta
DB_NAME=seice
```

#### Opção 2: Editar o Código

Altere as configurações diretamente no arquivo `main.go` na função `initDB()`.

### 4. Instalando Dependências

Execute o seguinte comando para instalar as dependências do projeto:

```bash
go mod tidy
```

### 5. Inicializando o Banco de Dados

O sistema criará automaticamente as tabelas necessárias e dados iniciais na primeira execução. Se preferir, você pode executar manualmente o script SQL fornecido:

```bash
mysql -u root < database/init.sql
```

## Executando o Sistema

Para iniciar o servidor, execute:

```bash
go run main.go
```

O servidor será iniciado na porta 8080 por padrão. Você pode acessar a aplicação em:

```
http://localhost:8080
```

## Estrutura da API

A API do sistema está disponível nos seguintes endpoints:

### Estagiários
- `GET /api/estagiarios` - Lista todos os estagiários
- `GET /api/estagiarios/{id}` - Obtém detalhes de um estagiário específico
- `POST /api/estagiarios` - Cria um novo estagiário
- `PUT /api/estagiarios/{id}` - Atualiza os dados de um estagiário
- `DELETE /api/estagiarios/{id}` - Remove um estagiário

### Presenças
- `GET /api/presencas` - Lista todos os registros de presença
- `GET /api/presencas/{id}` - Obtém detalhes de uma presença específica
- `POST /api/presencas` - Cria um novo registro de presença
- `PUT /api/presencas/{id}` - Atualiza um registro de presença
- `DELETE /api/presencas/{id}` - Remove um registro de presença
- `GET /api/presencas-hoje` - Lista as presenças do dia atual

### Entrada e Saída
- `POST /api/registrar-entrada` - Registra a entrada de um estagiário
- `POST /api/registrar-saida` - Registra a saída de um estagiário

### Relatórios
- `GET /api/relatorio` - Gera relatório com base em período especificado
- `GET /api/estatisticas` - Obtém estatísticas gerais do sistema

## Fluxo de Trabalho Típico

1. Cadastrar estagiários no sistema
2. Estagiários registram sua entrada ao chegar
3. Estagiários registram sua saída ao término do expediente
4. Administradores podem visualizar relatórios e estatísticas
5. Sistema calcula automaticamente horas trabalhadas

## Recursos Adicionais

- O sistema lida automaticamente com feriados cadastrados
- Validações para evitar registros duplicados ou inconsistentes
- Tratamento de erros e feedback claro para usuários
- Suporte para filtros em relatórios e listagens

## Desenvolvimento

Para contribuir ou estender o sistema:

1. O código do backend está organizado em torno das principais entidades (estagiários e presenças)
2. Os endpoints da API seguem princípios RESTful
3. O banco de dados inclui views e procedures para facilitar operações comuns
4. Triggers garantem a integridade dos cálculos de horas

