# Sistema de Presença de Estagiários - Colégio SEICE

Este sistema gerencia o registro de presença dos estagiários do Colégio SEICE em Duque de Caxias. Ele foi desenvolvido utilizando Go (Golang) para o backend e MySQL para o banco de dados.

## Requisitos

- Go 1.16+
- MySQL 5.7+ ou MariaDB 10.2+
- Git (opcional, para clonar o repositório)

## Bibliotecas utilizadas

- [gorilla/mux](https://github.com/gorilla/mux) - Roteador HTTP
- [go-sql-driver/mysql](https://github.com/go-sql-driver/mysql) - Driver MySQL para Go
- [joho/godotenv](https://github.com/joho/godotenv) - Carregamento de variáveis de ambiente

## Configuração

1. Clone o repositório:
   ```
   git clone [URL_DO_REPOSITORIO]
   cd sistema-presenca-estagiarios
   ```

2. Instale as dependências:
   ```
   go mod download
   ```

3. Configure o banco de dados:
   - Crie um banco de dados MySQL
   - Execute o script SQL localizado em `schema-bd.sql`

4. Configure as variáveis de ambiente:
   - Copie o arquivo `.env.example` para `.env`
   - Edite o arquivo `.env` com as credenciais do seu banco de dados

## Executando o sistema

```bash
go run main.go
```

O servidor será iniciado na porta especificada no arquivo `.env` (padrão: 8080).

## Estrutura da API

### Estagiários

- **GET /estagiarios** - Lista todos os estagiários
- **GET /estagiarios/{id}** - Obtém detalhes de um estagiário
- **POST /estagiarios** - Cadastra um novo estagiário
- **PUT /estagiarios/{id}** - Atualiza dados de um estagiário
- **DELETE /estagiarios/{id}** - Desativa um estagiário (soft delete)

### Presenças

- **GET /presencas** - Lista todos os registros de presença
- **GET /presencas/{id}** - Obtém detalhes de um registro de presença
- **POST /presencas** - Registra manualmente uma presença
- **PUT /presencas/{id}** - Atualiza um registro de presença
- **DELETE /presencas/{id}** - Remove um registro de presença
- **GET /presencas/estagiario/{estagiarioId}** - Lista presenças de um estagiário

### Registros de Entrada/Saída

- **POST /registrar-entrada/{estagiarioId}** - Registra entrada de um estagiário
- **PUT /registrar-saida/{estagiarioId}** - Registra saída de um estagiário

### Relatórios

- **GET /relatorios/mensal** - Gera relatório mensal de presenças
  - Parâmetros: `?mes=5&ano=2025` (opcional, usa o mês atual se não informado)

## Exemplos de uso

### Registrar um novo estagiário

```
POST /estagiarios
Content-Type: application/json

{
  "nome": "Novo Estagiário",
  "email": "novo.estagiario@seice.edu.br",
  "telefone": "(21) 99999-9999",
  "data_inicio": "2025-05-20"
}
```

### Registrar entrada de um estagiário

```
POST /registrar-entrada/1
Content-Type: application/json

{
  "observacao": "Chegou pontualmente"
}
```

### Registrar saída de um estagiário

```
PUT /registrar-saida/1
Content-Type: application/json

{
  "observacao": "Completou todas as tarefas"
}
```

### Obter relatório mensal

```
GET /relatorios/mensal?mes=5&ano=2025
```

## Expandindo o sistema

O sistema foi projetado para ser facilmente expansível. Algumas possíveis melhorias:

1. **Implementar autenticação** - Adicionar JWT para proteger as rotas
2. **Sistema de notificações** - Alertas por email ou SMS para atrasos
3. **Dashboard** - Implementar um frontend com estatísticas
4. **Exportação** - Permitir exportar relatórios em CSV ou PDF
5. **Perfis de acesso** - Diferenciar administradores de usuários comuns

