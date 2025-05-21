package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"

	_ "github.com/go-sql-driver/mysql"
	"github.com/joho/godotenv"
)

func main() {
	// Carregar variáveis de ambiente do arquivo .env
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Erro ao carregar o arquivo .env")
	}

	// Configurar conexão com o banco de dados
	dbUser := os.Getenv("DB_USER")
	dbPassword := os.Getenv("DB_PASSWORD")
	dbHost := os.Getenv("DB_HOST")
	dbPort := os.Getenv("DB_PORT")
	dbName := os.Getenv("DB_NAME")

	// String de conexão
	dsn := fmt.Sprintf("%s:%s@tcp(%s:%s)/%s", dbUser, dbPassword, dbHost, dbPort, dbName)

	// Abrir conexão
	db, err := sql.Open("mysql", dsn)
	if err != nil {
		log.Fatalf("Erro ao conectar ao banco de dados: %v", err)
	}
	defer db.Close()

	// Testar conexão
	err = db.Ping()
	if err != nil {
		log.Fatalf("Erro ao testar conexão: %v", err)
	}
	fmt.Println("Conexão com o banco de dados estabelecida com sucesso!")

	// Listar estagiários
	rows, err := db.Query("SELECT id, nome, email, telefone, data_inicio, ativo FROM estagiarios")
	if err != nil {
		log.Fatalf("Erro ao executar consulta: %v", err)
	}
	defer rows.Close()

	fmt.Println("\nLista de estagiários cadastrados:")
	fmt.Println("----------------------------------")

	for rows.Next() {
		var id int
		var nome, email, telefone, dataInicio string
		var ativo bool

		err := rows.Scan(&id, &nome, &email, &telefone, &dataInicio, &ativo)
		if err != nil {
			log.Fatalf("Erro ao ler dados: %v", err)
		}

		status := "Ativo"
		if !ativo {
			status = "Inativo"
		}

		fmt.Printf("ID: %d | Nome: %s | Email: %s | Telefone: %s | Data Início: %s | Status: %s\n",
			id, nome, email, telefone, dataInicio, status)
	}

	fmt.Println("\nTeste concluído com sucesso!")
}
