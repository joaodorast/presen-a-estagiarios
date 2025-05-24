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

- **Backend**: Django (Python)
- **Banco de Dados**: SQLite
- **API**: RESTful com Django REST Framework
- **Frontend**: HTML, CSS e JavaScript (servido pelo backend)

## Requisitos

- Python 3.8 ou superior
- Pip (gerenciador de pacotes Python)
- Sistema operacional compatível (Windows, macOS, Linux)

## Instalação e Configuração

### 1. Preparando o Ambiente

Primeiro, certifique-se de ter Python instalado em seu sistema.

#### Instalando Python (se necessário)

Faça o download e instale Python a partir do [site oficial](https://www.python.org/downloads/).

### 2. Clonando o Repositório

```bash
git clone https://github.com/joaodorast/presen-a-estagiarios.git
cd presen-a-estagiarios
```

### 3. Criando o Ambiente Virtual

```bash
python -m venv venv
```

Ative o ambiente virtual:

- **Windows**:
  ```bash
  venv\Scripts\activate
  ```
- **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

### 4. Instalando Dependências

```bash
pip install -r requirements.txt
```

### 5. Migrando o Banco de Dados

```bash
python manage.py migrate
```

### 6. Criando um Superusuário (opcional)

```bash
python manage.py createsuperuser
```

## Executando o Sistema

Para iniciar o servidor de desenvolvimento, execute:

```bash
python manage.py runserver
```

O servidor será iniciado na porta 8000 por padrão. Você pode acessar a aplicação em:

```
http://localhost:8000
```

## Estrutura da API

A API do sistema está disponível nos seguintes endpoints (exemplo):

### Estagiários
- `GET /api/estagiarios/` - Lista todos os estagiários
- `GET /api/estagiarios/{id}/` - Obtém detalhes de um estagiário específico
- `POST /api/estagiarios/` - Cria um novo estagiário
- `PUT /api/estagiarios/{id}/` - Atualiza os dados de um estagiário
- `DELETE /api/estagiarios/{id}/` - Remove um estagiário

### Presenças
- `GET /api/presencas/` - Lista todos os registros de presença
- `GET /api/presencas/{id}/` - Obtém detalhes de uma presença específica
- `POST /api/presencas/` - Cria um novo registro de presença
- `PUT /api/presencas/{id}/` - Atualiza um registro de presença
- `DELETE /api/presencas/{id}/` - Remove um registro de presença
- `GET /api/presencas-hoje/` - Lista as presenças do dia atual

### Entrada e Saída
- `POST /api/registrar-entrada/` - Registra a entrada de um estagiário
- `POST /api/registrar-saida/` - Registra a saída de um estagiário

### Relatórios
- `GET /api/relatorio/` - Gera relatório com base em período especificado
- `GET /api/estatisticas/` - Obtém estatísticas gerais do sistema

## Fluxo de Trabalho Típico

1. Cadastrar estagiários no sistema
2. Estagiários registram sua entrada ao chegar
3. Estagiários registram sua saída ao término do expediente
4. Administradores podem visualizar relatórios e estatísticas
5. Sistema calcula automaticamente horas trabalhadas

## Recursos Adicionais

- Validações para evitar registros duplicados ou inconsistentes
- Tratamento de erros e feedback claro para usuários
- Suporte para filtros em relatórios e listagens

## Desenvolvimento

Para contribuir ou estender o sistema:

1. O código do backend está organizado em torno das principais entidades (estagiários e presenças)
2. Os endpoints da API seguem princípios RESTful
3. O banco de dados utiliza SQLite por padrão para facilitar o desenvolvimento
4. O Django Admin pode ser usado para gerenciar dados facilmente