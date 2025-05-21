package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"

	_ "github.com/go-sql-driver/mysql"
	"github.com/gorilla/mux"
	"github.com/joho/godotenv"
)

type Estagiario struct {
	ID         int    `json:"id"`
	Nome       string `json:"nome"`
	Email      string `json:"email"`
	Telefone   string `json:"telefone"`
	DataInicio string `json:"dataInicio"`
	Ativo      bool   `json:"ativo"`
}

type Presenca struct {
	ID             int    `json:"id"`
	EstagiarioID   int    `json:"estagiarioId"`
	NomeEstagiario string `json:"nomeEstagiario,omitempty"`
	Data           string `json:"data"`
	Entrada        string `json:"entrada"`
	Saida          string `json:"saida,omitempty"`
	Horas          string `json:"horas,omitempty"`
	Observacao     string `json:"observacao,omitempty"`
}

type RelatorioItem struct {
	Nome           string  `json:"nome"`
	TotalPresencas int     `json:"totalPresencas"`
	TotalHoras     float64 `json:"totalHoras"`
	MediaDiaria    float64 `json:"mediaDiaria"`
}

type RelatorioDados struct {
	TotalPresencas int             `json:"totalPresencas"`
	MediaHoras     float64         `json:"mediaHoras"`
	TotalHoras     float64         `json:"totalHoras"`
	Estagiarios    []RelatorioItem `json:"estagiarios"`
}

var db *sql.DB

func main() {
	// Carregar variáveis de ambiente se existirem
	_ = godotenv.Load()

	initDB()
	defer db.Close()

	err := checkDBInit()
	if err != nil {
		log.Printf("Inicializando banco de dados: %v\n", err)
		if err = initializeDB(); err != nil {
			log.Fatalf("Falha ao inicializar banco de dados: %v", err)
		}
	}

	r := mux.NewRouter()

	r.Use(corsMiddleware)
	r.Use(loggingMiddleware)

	r.HandleFunc("/api/estagiarios", getEstagiarios).Methods("GET")
	r.HandleFunc("/api/estagiarios/{id}", getEstagiario).Methods("GET")
	r.HandleFunc("/api/estagiarios", createEstagiario).Methods("POST")
	r.HandleFunc("/api/estagiarios/{id}", updateEstagiario).Methods("PUT")
	r.HandleFunc("/api/estagiarios/{id}", deleteEstagiario).Methods("DELETE")

	r.HandleFunc("/api/presencas", getPresencas).Methods("GET")
	r.HandleFunc("/api/presencas/{id}", getPresenca).Methods("GET")
	r.HandleFunc("/api/presencas", createPresenca).Methods("POST")
	r.HandleFunc("/api/presencas/{id}", updatePresenca).Methods("PUT")
	r.HandleFunc("/api/presencas/{id}", deletePresenca).Methods("DELETE")
	r.HandleFunc("/api/presencas-hoje", getPresencasHoje).Methods("GET")

	r.HandleFunc("/api/registrar-entrada", registrarEntrada).Methods("POST")
	r.HandleFunc("/api/registrar-saida", registrarSaida).Methods("POST")

	r.HandleFunc("/api/relatorio", getRelatorio).Methods("GET")

	r.HandleFunc("/api/estatisticas", getEstatisticas).Methods("GET")

	r.PathPrefix("/").Handler(http.FileServer(http.Dir("./public")))

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	log.Printf("Servidor iniciado na porta %s\n", port)
	log.Fatal(http.ListenAndServe(":"+port, r))
}

func initDB() {

	dbUser := "root"
	dbPass := ""
	dbHost := "localhost"
	dbPort := "3306"
	dbName := "seice"

	// Sobrescrever com variáveis de ambiente, se existirem
	if env := os.Getenv("DB_USER"); env != "" {
		dbUser = env
	}
	if env := os.Getenv("DB_PASS"); env != "" {
		dbPass = env
	}
	if env := os.Getenv("DB_HOST"); env != "" {
		dbHost = env
	}
	if env := os.Getenv("DB_PORT"); env != "" {
		dbPort = env
	}
	if env := os.Getenv("DB_NAME"); env != "" {
		dbName = env
	}

	dataSourceName := dbUser + ":" + dbPass + "@tcp(" + dbHost + ":" + dbPort + ")/" + dbName

	var err error
	db, err = sql.Open("mysql", dataSourceName)
	if err != nil {
		log.Fatalf("Erro ao conectar ao banco de dados: %v", err)
	}

	err = db.Ping()
	if err != nil {
		log.Fatalf("Erro ao testar conexão com o banco de dados: %v", err)
	}

	db.SetMaxOpenConns(10)
	db.SetMaxIdleConns(5)
	db.SetConnMaxLifetime(time.Minute * 5)
}

func checkDBInit() error {
	var count int
	err := db.QueryRow("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'estagiarios'").Scan(&count)
	if err != nil {
		return err
	}
	if count == 0 {
		return err
	}
	return nil
}

func initializeDB() error {

	_, err := db.Exec(`
	CREATE TABLE IF NOT EXISTS estagiarios (
		id INT AUTO_INCREMENT PRIMARY KEY,
		nome VARCHAR(100) NOT NULL,
		email VARCHAR(100) NOT NULL,
		telefone VARCHAR(20) NOT NULL,
		data_inicio DATE NOT NULL,
		ativo BOOLEAN NOT NULL DEFAULT TRUE
	)`)
	if err != nil {
		return err
	}

	_, err = db.Exec(`
	CREATE TABLE IF NOT EXISTS presencas (
		id INT AUTO_INCREMENT PRIMARY KEY,
		estagiario_id INT NOT NULL,
		data DATE NOT NULL,
		entrada TIME NOT NULL,
		saida TIME NULL,
		horas VARCHAR(10) NULL,
		observacao TEXT NULL,
		FOREIGN KEY (estagiario_id) REFERENCES estagiarios(id)
	)`)
	if err != nil {
		return err
	}

	estagiarios := []Estagiario{
		{Nome: "João Pedro", Email: "joaopedro@gmail.com", Telefone: "(21) 98765-4321", DataInicio: "2024-02-15", Ativo: true},
		{Nome: "Maria Clara", Email: "mariaclara@gmail.com", Telefone: "(21) 91234-5678", DataInicio: "2024-03-01", Ativo: true},
		{Nome: "Miguel Combas", Email: "miguelcombas@gmail.com", Telefone: "(21) 99876-5432", DataInicio: "2023-11-10", Ativo: true},
		{Nome: "Eloá Christine", Email: "eloacristine@gmail.com", Telefone: "(21) 95555-4444", DataInicio: "2024-01-20", Ativo: false},
		{Nome: "Pedro Henricky", Email: "pedrohenricky@gmail.com", Telefone: "(21) 93333-2222", DataInicio: "2023-10-05", Ativo: true},
	}

	for _, e := range estagiarios {
		_, err = db.Exec(`
		INSERT INTO estagiarios (nome, email, telefone, data_inicio, ativo)
		VALUES (?, ?, ?, ?, ?)`,
			e.Nome, e.Email, e.Telefone, e.DataInicio, e.Ativo)
		if err != nil {
			return err
		}
	}

	presencas := []struct {
		estagiarioID int
		data         string
		entrada      string
		saida        string
		observacao   string
	}{
		{1, "2024-05-19", "08:05:00", "17:15:00", ""},
		{2, "2024-05-19", "08:30:00", "17:30:00", ""},
		{3, "2024-05-19", "08:15:00", "17:00:00", ""},
		{1, "2024-05-18", "08:00:00", "17:00:00", ""},
		{2, "2024-05-18", "08:30:00", "17:30:00", ""},
		{5, "2024-05-18", "09:00:00", "18:00:00", ""},
		{1, "2024-05-17", "08:10:00", "17:05:00", ""},
		{3, "2024-05-17", "08:20:00", "17:15:00", ""},
		{5, "2024-05-17", "08:45:00", "17:50:00", ""},
	}

	for _, p := range presencas {

		layout := "15:04:05"
		entrada, _ := time.Parse(layout, p.entrada)
		saida, _ := time.Parse(layout, p.saida)
		diff := saida.Sub(entrada)
		hours := int(diff.Hours())
		minutes := int(diff.Minutes()) % 60
		horas := fmt.Sprintf("%d:%02d", hours, minutes)

		_, err = db.Exec(`
		INSERT INTO presencas (estagiario_id, data, entrada, saida, horas, observacao)
		VALUES (?, ?, ?, ?, ?, ?)`,
			p.estagiarioID, p.data, p.entrada, p.saida, horas, p.observacao)
		if err != nil {
			return err
		}
	}

	return nil
}

func corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		next.ServeHTTP(w, r)
	})
}

func loggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		log.Printf("[%s] %s", r.Method, r.RequestURI)
		next.ServeHTTP(w, r)
	})
}

func getEstagiarios(w http.ResponseWriter, r *http.Request) {
	rows, err := db.Query(`SELECT id, nome, email, telefone, data_inicio, ativo FROM estagiarios`)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	estagiarios := []Estagiario{}
	for rows.Next() {
		var e Estagiario
		var dataInicio sql.NullString
		if err := rows.Scan(&e.ID, &e.Nome, &e.Email, &e.Telefone, &dataInicio, &e.Ativo); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		if dataInicio.Valid {
			e.DataInicio = dataInicio.String
		}
		estagiarios = append(estagiarios, e)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(estagiarios)
}

func getEstagiario(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id, err := strconv.Atoi(vars["id"])
	if err != nil {
		http.Error(w, "ID inválido", http.StatusBadRequest)
		return
	}

	var e Estagiario
	var dataInicio sql.NullString
	err = db.QueryRow(`SELECT id, nome, email, telefone, data_inicio, ativo FROM estagiarios WHERE id = ?`, id).
		Scan(&e.ID, &e.Nome, &e.Email, &e.Telefone, &dataInicio, &e.Ativo)
	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Estagiário não encontrado", http.StatusNotFound)
		} else {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
		return
	}

	if dataInicio.Valid {
		e.DataInicio = dataInicio.String
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(e)
}

func createEstagiario(w http.ResponseWriter, r *http.Request) {
	var e Estagiario
	if err := json.NewDecoder(r.Body).Decode(&e); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	result, err := db.Exec(`
		INSERT INTO estagiarios (nome, email, telefone, data_inicio, ativo)
		VALUES (?, ?, ?, ?, ?)`,
		e.Nome, e.Email, e.Telefone, e.DataInicio, e.Ativo)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	id, _ := result.LastInsertId()
	e.ID = int(id)

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(e)
}

func updateEstagiario(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id, err := strconv.Atoi(vars["id"])
	if err != nil {
		http.Error(w, "ID inválido", http.StatusBadRequest)
		return
	}

	var e Estagiario
	if err := json.NewDecoder(r.Body).Decode(&e); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	_, err = db.Exec(`
		UPDATE estagiarios
		SET nome = ?, email = ?, telefone = ?, data_inicio = ?, ativo = ?
		WHERE id = ?`,
		e.Nome, e.Email, e.Telefone, e.DataInicio, e.Ativo, id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	e.ID = id
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(e)
}

func deleteEstagiario(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id, err := strconv.Atoi(vars["id"])
	if err != nil {
		http.Error(w, "ID inválido", http.StatusBadRequest)
		return
	}

	var count int
	err = db.QueryRow("SELECT COUNT(*) FROM presencas WHERE estagiario_id = ?", id).Scan(&count)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	if count > 0 {
		http.Error(w, "Não é possível excluir este estagiário pois há presenças registradas", http.StatusConflict)
		return
	}

	_, err = db.Exec("DELETE FROM estagiarios WHERE id = ?", id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}

func getPresencas(w http.ResponseWriter, r *http.Request) {

	estagiarioID := r.URL.Query().Get("estagiarioId")
	dataInicio := r.URL.Query().Get("dataInicio")
	dataFim := r.URL.Query().Get("dataFim")

	query := `
		SELECT p.id, p.estagiario_id, e.nome, p.data, p.entrada, p.saida, p.horas, p.observacao
		FROM presencas p
		JOIN estagiarios e ON p.estagiario_id = e.id
		WHERE 1=1`
	var args []interface{}

	if estagiarioID != "" {
		query += " AND p.estagiario_id = ?"
		args = append(args, estagiarioID)
	}
	if dataInicio != "" {
		query += " AND p.data >= ?"
		args = append(args, dataInicio)
	}
	if dataFim != "" {
		query += " AND p.data <= ?"
		args = append(args, dataFim)
	}

	query += " ORDER BY p.data DESC, p.entrada DESC"

	rows, err := db.Query(query, args...)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	presencas := []Presenca{}
	for rows.Next() {
		var p Presenca
		var saida, horas, observacao sql.NullString
		var nome string
		if err := rows.Scan(&p.ID, &p.EstagiarioID, &nome, &p.Data, &p.Entrada, &saida, &horas, &observacao); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		p.NomeEstagiario = nome
		if saida.Valid {
			p.Saida = saida.String
		}
		if horas.Valid {
			p.Horas = horas.String
		}
		if observacao.Valid {
			p.Observacao = observacao.String
		}
		presencas = append(presencas, p)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(presencas)
}

func getPresenca(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id, err := strconv.Atoi(vars["id"])
	if err != nil {
		http.Error(w, "ID inválido", http.StatusBadRequest)
		return
	}

	var p Presenca
	var saida, horas, observacao sql.NullString
	var nome string
	err = db.QueryRow(`
		SELECT p.id, p.estagiario_id, e.nome, p.data, p.entrada, p.saida, p.horas, p.observacao
		FROM presencas p
		JOIN estagiarios e ON p.estagiario_id = e.id
		WHERE p.id = ?`, id).Scan(&p.ID, &p.EstagiarioID, &nome, &p.Data, &p.Entrada, &saida, &horas, &observacao)
	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Presença não encontrada", http.StatusNotFound)
		} else {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
		return
	}

	p.NomeEstagiario = nome
	if saida.Valid {
		p.Saida = saida.String
	}
	if horas.Valid {
		p.Horas = horas.String
	}
	if observacao.Valid {
		p.Observacao = observacao.String
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(p)
}

func createPresenca(w http.ResponseWriter, r *http.Request) {
	var p Presenca
	if err := json.NewDecoder(r.Body).Decode(&p); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	var horas string
	if p.Saida != "" {
		horas = calcularHoras(p.Entrada, p.Saida)
		p.Horas = horas
	}

	result, err := db.Exec(`
		INSERT INTO presencas (estagiario_id, data, entrada, saida, horas, observacao)
		VALUES (?, ?, ?, ?, ?, ?)`,
		p.EstagiarioID, p.Data, p.Entrada, p.Saida, p.Horas, p.Observacao)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	id, _ := result.LastInsertId()
	p.ID = int(id)

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(p)
}

func updatePresenca(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id, err := strconv.Atoi(vars["id"])
	if err != nil {
		http.Error(w, "ID inválido", http.StatusBadRequest)
		return
	}

	var p Presenca
	if err := json.NewDecoder(r.Body).Decode(&p); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	if p.Saida != "" && p.Entrada != "" {
		p.Horas = calcularHoras(p.Entrada, p.Saida)
	}

	_, err = db.Exec(`
		UPDATE presencas
		SET estagiario_id = ?, data = ?, entrada = ?, saida = ?, horas = ?, observacao = ?
		WHERE id = ?`,
		p.EstagiarioID, p.Data, p.Entrada, p.Saida, p.Horas, p.Observacao, id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	p.ID = id
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(p)
}

func deletePresenca(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id, err := strconv.Atoi(vars["id"])
	if err != nil {
		http.Error(w, "ID inválido", http.StatusBadRequest)
		return
	}

	_, err = db.Exec("DELETE FROM presencas WHERE id = ?", id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}

func getPresencasHoje(w http.ResponseWriter, r *http.Request) {
	hoje := time.Now().Format("2006-01-02")

	rows, err := db.Query(`
		SELECT p.id, p.estagiario_id, e.nome, p.data, p.entrada, p.saida, p.horas, p.observacao
		FROM presencas p
		JOIN estagiarios e ON p.estagiario_id = e.id
		WHERE p.data = ?
		ORDER BY p.entrada DESC`, hoje)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	presencas := []Presenca{}
	for rows.Next() {
		var p Presenca
		var saida, horas, observacao sql.NullString
		var nome string
		if err := rows.Scan(&p.ID, &p.EstagiarioID, &nome, &p.Data, &p.Entrada, &saida, &horas, &observacao); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		p.NomeEstagiario = nome
		if saida.Valid {
			p.Saida = saida.String
		}
		if horas.Valid {
			p.Horas = horas.String
		}
		if observacao.Valid {
			p.Observacao = observacao.String
		}
		presencas = append(presencas, p)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(presencas)
}

func registrarEntrada(w http.ResponseWriter, r *http.Request) {
	var data struct {
		EstagiarioID int    `json:"estagiarioId"`
		Observacao   string `json:"observacao"`
	}

	if err := json.NewDecoder(r.Body).Decode(&data); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	var ativo bool
	err := db.QueryRow("SELECT ativo FROM estagiarios WHERE id = ?", data.EstagiarioID).Scan(&ativo)
	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Estagiário não encontrado", http.StatusNotFound)
		} else {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
		return
	}

	if !ativo {
		http.Error(w, "Estagiário inativo", http.StatusBadRequest)
		return
	}

	hoje := time.Now().Format("2006-01-02")
	var count int
	err = db.QueryRow("SELECT COUNT(*) FROM presencas WHERE estagiario_id = ? AND data = ?", data.EstagiarioID, hoje).Scan(&count)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	if count > 0 {
		http.Error(w, "Este estagiário já registrou entrada hoje", http.StatusConflict)
		return
	}

	horaAtual := time.Now().Format("15:04:05")
	result, err := db.Exec(`
		INSERT INTO presencas (estagiario_id, data, entrada, observacao)
		VALUES (?, ?, ?, ?)`,
		data.EstagiarioID, hoje, horaAtual, data.Observacao)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	id, _ := result.LastInsertId()

	var p Presenca
	var nome string
	err = db.QueryRow(`
		SELECT p.id, p.estagiario_id, e.nome, p.data, p.entrada, p.observacao
		FROM presencas p
		JOIN estagiarios e ON p.estagiario_id = e.id
		WHERE p.id = ?`, id).Scan(&p.ID, &p.EstagiarioID, &nome, &p.Data, &p.Entrada, &p.Observacao)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	p.NomeEstagiario = nome

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(p)
}

func registrarSaida(w http.ResponseWriter, r *http.Request) {
	var data struct {
		EstagiarioID int    `json:"estagiarioId"`
		Observacao   string `json:"observacao"`
	}

	if err := json.NewDecoder(r.Body).Decode(&data); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	hoje := time.Now().Format("2006-01-02")
	var presencaID int
	var entrada string
	var observacaoAtual sql.NullString

	err := db.QueryRow(`
		SELECT id, entrada, observacao FROM presencas 
		WHERE estagiario_id = ? AND data = ? AND saida IS NULL`,
		data.EstagiarioID, hoje).Scan(&presencaID, &entrada, &observacaoAtual)

	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Não há entrada aberta para este estagiário hoje", http.StatusNotFound)
		} else {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
		return
	}

	horaAtual := time.Now().Format("15:04:05")

	horas := calcularHoras(entrada, horaAtual)

	var observacaoFinal string
	if observacaoAtual.Valid && observacaoAtual.String != "" {
		if data.Observacao != "" {
			observacaoFinal = observacaoAtual.String + " | Saída: " + data.Observacao
		} else {
			observacaoFinal = observacaoAtual.String
		}
	} else {
		observacaoFinal = data.Observacao
	}

	_, err = db.Exec(`
		UPDATE presencas
		SET saida = ?, horas = ?, observacao = ?
		WHERE id = ?`,
		horaAtual, horas, observacaoFinal, presencaID)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	var p Presenca
	var nome string
	var saida, horasDB, observacao sql.NullString

	err = db.QueryRow(`
		SELECT p.id, p.estagiario_id, e.nome, p.data, p.entrada, p.saida, p.horas, p.observacao
		FROM presencas p
		JOIN estagiarios e ON p.estagiario_id = e.id
		WHERE p.id = ?`, presencaID).Scan(&p.ID, &p.EstagiarioID, &nome, &p.Data, &p.Entrada, &saida, &horasDB, &observacao)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	p.NomeEstagiario = nome
	if saida.Valid {
		p.Saida = saida.String
	}
	if horasDB.Valid {
		p.Horas = horasDB.String
	}
	if observacao.Valid {
		p.Observacao = observacao.String
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(p)
}

func calcularHoras(entrada, saida string) string {
	layout := "15:04:05"
	entradaTime, _ := time.Parse(layout, entrada)
	saidaTime, _ := time.Parse(layout, saida)

	diff := saidaTime.Sub(entradaTime)

	hours := int(diff.Hours())
	minutes := int(diff.Minutes()) % 60

	return fmt.Sprintf("%d:%02d", hours, minutes)
}

func getRelatorio(w http.ResponseWriter, r *http.Request) {

	dataInicio := r.URL.Query().Get("dataInicio")
	dataFim := r.URL.Query().Get("dataFim")

	if dataInicio == "" || dataFim == "" {
		http.Error(w, "Data de início e fim são obrigatórias", http.StatusBadRequest)
		return
	}

	var totalPresencas int
	var totalHorasStr string

	query := `
		SELECT COUNT(*), SUM(TIME_TO_SEC(horas))/3600
		FROM presencas 
		WHERE data BETWEEN ? AND ?
		AND saida IS NOT NULL`

	err := db.QueryRow(query, dataInicio, dataFim).Scan(&totalPresencas, &totalHorasStr)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	totalHoras, _ := strconv.ParseFloat(totalHorasStr, 64)

	mediaHoras := 0.0
	if totalPresencas > 0 {
		mediaHoras = totalHoras / float64(totalPresencas)
	}

	rows, err := db.Query(`
		SELECT e.nome, 
		       COUNT(p.id) as total_presencas,
		       SUM(TIME_TO_SEC(p.horas))/3600 as total_horas
		FROM estagiarios e
		JOIN presencas p ON e.id = p.estagiario_id
		WHERE p.data BETWEEN ? AND ?
		AND p.saida IS NOT NULL
		GROUP BY e.id
		ORDER BY e.nome`, dataInicio, dataFim)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	estagiarios := []RelatorioItem{}
	for rows.Next() {
		var item RelatorioItem
		var totalHorasEst float64
		if err := rows.Scan(&item.Nome, &item.TotalPresencas, &totalHorasEst); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		item.TotalHoras = totalHorasEst
		if item.TotalPresencas > 0 {
			item.MediaDiaria = item.TotalHoras / float64(item.TotalPresencas)
		}

		estagiarios = append(estagiarios, item)
	}

	resultado := RelatorioDados{
		TotalPresencas: totalPresencas,
		TotalHoras:     totalHoras,
		MediaHoras:     mediaHoras,
		Estagiarios:    estagiarios,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resultado)
}

func getEstatisticas(w http.ResponseWriter, r *http.Request) {
	hoje := time.Now().Format("2006-01-02")

	var dados struct {
		TotalEstagiarios           int `json:"totalEstagiarios"`
		EstagiariosPresentesHoje   int `json:"estagiariosPresentesHoje"`
		EstagiariosPresentesOntem  int `json:"estagiariosPresentesOntem"`
		EstagiariosPresentesSemana int `json:"estagiariosPresentesSemana"`
	}

	err := db.QueryRow("SELECT COUNT(*) FROM estagiarios WHERE ativo = TRUE").Scan(&dados.TotalEstagiarios)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// Estagiários presentes hoje
	err = db.QueryRow("SELECT COUNT(DISTINCT estagiario_id) FROM presencas WHERE data = ?", hoje).Scan(&dados.EstagiariosPresentesHoje)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// Estagiários presentes ontem
	ontem := time.Now().AddDate(0, 0, -1).Format("2006-01-02")
	err = db.QueryRow("SELECT COUNT(DISTINCT estagiario_id) FROM presencas WHERE data = ?", ontem).Scan(&dados.EstagiariosPresentesOntem)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	umaSemanaAtras := time.Now().AddDate(0, 0, -7).Format("2006-01-02")
	err = db.QueryRow("SELECT COUNT(DISTINCT estagiario_id) FROM presencas WHERE data BETWEEN ? AND ?", umaSemanaAtras, hoje).Scan(&dados.EstagiariosPresentesSemana)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(dados)
}

func parseTime(hora string) (time.Time, error) {
	layout := "15:04:05"
	return time.Parse(layout, hora)
}

func formatarDataHora(data, hora string) (time.Time, error) {
	layout := "2006-01-02 15:04:05"
	return time.Parse(layout, data+" "+hora)
}

func checkErr(err error) {
	if err != nil {
		log.Fatal(err)
	}
}
