package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/go-sql-driver/mysql"
	"github.com/gorilla/mux"
	"github.com/joho/godotenv"
)

// Estagiário representa a estrutura de dados de um estagiário
type Estagiario struct {
	ID         int    `json:"id"`
	Nome       string `json:"nome"`
	Email      string `json:"email"`
	Telefone   string `json:"telefone"`
	DataInicio string `json:"data_inicio"`
	Ativo      bool   `json:"ativo"`
}

// Presença representa a estrutura de dados de uma presença
type Presenca struct {
	ID           int    `json:"id"`
	EstagiarioID int    `json:"estagiario_id"`
	Data         string `json:"data"`
	HoraEntrada  string `json:"hora_entrada"`
	HoraSaida    string `json:"hora_saida"`
	Observacao   string `json:"observacao"`
}

// PresencaCompleta contém dados de presença e do estagiário
type PresencaCompleta struct {
	Presenca   Presenca   `json:"presenca"`
	Estagiario Estagiario `json:"estagiario"`
}

// RelatorioMensal representa estatísticas mensais de presença
type RelatorioMensal struct {
	EstagiarioID   int     `json:"estagiario_id"`
	NomeEstagiario string  `json:"nome_estagiario"`
	Mes            int     `json:"mes"`
	Ano            int     `json:"ano"`
	TotalPresencas int     `json:"total_presencas"`
	TotalHoras     float64 `json:"total_horas"`
}

// App encapsula a aplicação e suas dependências
type App struct {
	Router *mux.Router
	DB     *sql.DB
}

// Inicializa a aplicação com configurações do banco de dados e rotas
func (a *App) Initialize() {
	err := godotenv.Load()
	if err != nil {
		log.Println("Arquivo .env não encontrado, usando variáveis de ambiente")
	}

	dbUser := getEnv("DB_USER", "root")
	dbPassword := getEnv("DB_PASSWORD", "password")
	dbHost := getEnv("DB_HOST", "localhost")
	dbPort := getEnv("DB_PORT", "3306")
	dbName := getEnv("DB_NAME", "seice_estagiarios")

	// Configuração de conexão com o MySQL
	cfg := mysql.Config{
		User:                 dbUser,
		Passwd:               dbPassword,
		Net:                  "tcp",
		Addr:                 fmt.Sprintf("%s:%s", dbHost, dbPort),
		DBName:               dbName,
		AllowNativePasswords: true,
		ParseTime:            true,
	}

	// Abre a conexão com o banco de dados
	var dbErr error
	a.DB, dbErr = sql.Open("mysql", cfg.FormatDSN())
	if dbErr != nil {
		log.Fatalf("Erro ao conectar ao banco de dados: %v", dbErr)
	}

	// Testa a conexão com o banco de dados
	if err := a.DB.Ping(); err != nil {
		log.Fatalf("Erro ao conectar ao banco de dados: %v", err)
	}

	log.Println("Conexão com o banco de dados estabelecida com sucesso!")

	// Inicializa o router
	a.Router = mux.NewRouter()
	a.setupRoutes()
}

// Função helper para obter variáveis de ambiente
func getEnv(key, fallback string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return fallback
}

// Configura as rotas da API
func (a *App) setupRoutes() {
	// Rotas para estagiários
	a.Router.HandleFunc("/estagiarios", a.getEstagiarios).Methods("GET")
	a.Router.HandleFunc("/estagiarios/{id}", a.getEstagiario).Methods("GET")
	a.Router.HandleFunc("/estagiarios", a.createEstagiario).Methods("POST")
	a.Router.HandleFunc("/estagiarios/{id}", a.updateEstagiario).Methods("PUT")
	a.Router.HandleFunc("/estagiarios/{id}", a.deleteEstagiario).Methods("DELETE")

	// Rotas para presença
	a.Router.HandleFunc("/presencas", a.getPresencas).Methods("GET")
	a.Router.HandleFunc("/presencas/{id}", a.getPresenca).Methods("GET")
	a.Router.HandleFunc("/presencas", a.registrarPresenca).Methods("POST")
	a.Router.HandleFunc("/presencas/{id}", a.updatePresenca).Methods("PUT")
	a.Router.HandleFunc("/presencas/{id}", a.deletePresenca).Methods("DELETE")
	a.Router.HandleFunc("/presencas/estagiario/{estagiarioId}", a.getPresencasByEstagiario).Methods("GET")

	// Rotas para marcar entrada e saída
	a.Router.HandleFunc("/registrar-entrada/{estagiarioId}", a.registrarEntrada).Methods("POST")
	a.Router.HandleFunc("/registrar-saida/{estagiarioId}", a.registrarSaida).Methods("PUT")

	// Rota para relatório mensal
	a.Router.HandleFunc("/relatorios/mensal", a.getRelatorioMensal).Methods("GET")
}

// Inicia o servidor HTTP
func (a *App) Run(addr string) {
	log.Printf("Servidor iniciado na porta %s", addr)
	log.Fatal(http.ListenAndServe(addr, a.Router))
}

// Funções handlers para estagiários
func (a *App) getEstagiarios(w http.ResponseWriter, r *http.Request) {
	estagiarios := []Estagiario{}

	rows, err := a.DB.Query("SELECT id, nome, email, telefone, data_inicio, ativo FROM estagiarios")
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}
	defer rows.Close()

	for rows.Next() {
		var e Estagiario
		if err := rows.Scan(&e.ID, &e.Nome, &e.Email, &e.Telefone, &e.DataInicio, &e.Ativo); err != nil {
			respondWithError(w, http.StatusInternalServerError, err.Error())
			return
		}
		estagiarios = append(estagiarios, e)
	}

	respondWithJSON(w, http.StatusOK, estagiarios)
}

func (a *App) getEstagiario(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id := vars["id"]

	var e Estagiario
	err := a.DB.QueryRow("SELECT id, nome, email, telefone, data_inicio, ativo FROM estagiarios WHERE id = ?", id).
		Scan(&e.ID, &e.Nome, &e.Email, &e.Telefone, &e.DataInicio, &e.Ativo)

	if err != nil {
		if err == sql.ErrNoRows {
			respondWithError(w, http.StatusNotFound, "Estagiário não encontrado")
		} else {
			respondWithError(w, http.StatusInternalServerError, err.Error())
		}
		return
	}

	respondWithJSON(w, http.StatusOK, e)
}

func (a *App) createEstagiario(w http.ResponseWriter, r *http.Request) {
	var e Estagiario
	decoder := json.NewDecoder(r.Body)
	if err := decoder.Decode(&e); err != nil {
		respondWithError(w, http.StatusBadRequest, "Requisição inválida")
		return
	}
	defer r.Body.Close()

	// Definir data de início como data atual se não fornecida
	if e.DataInicio == "" {
		e.DataInicio = time.Now().Format("2006-01-02")
	}

	stmt, err := a.DB.Prepare("INSERT INTO estagiarios(nome, email, telefone, data_inicio, ativo) VALUES(?, ?, ?, ?, ?)")
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}
	defer stmt.Close()

	res, err := stmt.Exec(e.Nome, e.Email, e.Telefone, e.DataInicio, true)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}

	id, err := res.LastInsertId()
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}

	e.ID = int(id)
	e.Ativo = true
	respondWithJSON(w, http.StatusCreated, e)
}

func (a *App) updateEstagiario(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id := vars["id"]

	var e Estagiario
	decoder := json.NewDecoder(r.Body)
	if err := decoder.Decode(&e); err != nil {
		respondWithError(w, http.StatusBadRequest, "Requisição inválida")
		return
	}
	defer r.Body.Close()

	stmt, err := a.DB.Prepare("UPDATE estagiarios SET nome = ?, email = ?, telefone = ?, data_inicio = ?, ativo = ? WHERE id = ?")
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}
	defer stmt.Close()

	_, err = stmt.Exec(e.Nome, e.Email, e.Telefone, e.DataInicio, e.Ativo, id)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}

	respondWithJSON(w, http.StatusOK, e)
}

func (a *App) deleteEstagiario(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id := vars["id"]

	stmt, err := a.DB.Prepare("UPDATE estagiarios SET ativo = false WHERE id = ?")
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}
	defer stmt.Close()

	res, err := stmt.Exec(id)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}

	count, err := res.RowsAffected()
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}

	if count == 0 {
		respondWithError(w, http.StatusNotFound, "Estagiário não encontrado")
		return
	}

	respondWithJSON(w, http.StatusOK, map[string]string{"result": "success"})
}

// Funções handlers para presenças
func (a *App) getPresencas(w http.ResponseWriter, r *http.Request) {
	presencas := []PresencaCompleta{}

	query := `
		SELECT p.id, p.estagiario_id, p.data, p.hora_entrada, p.hora_saida, p.observacao, 
               e.id, e.nome, e.email, e.telefone, e.data_inicio, e.ativo
		FROM presencas p
		JOIN estagiarios e ON p.estagiario_id = e.id
		ORDER BY p.data DESC, p.hora_entrada DESC
	`

	rows, err := a.DB.Query(query)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}
	defer rows.Close()

	for rows.Next() {
		var pc PresencaCompleta
		if err := rows.Scan(
			&pc.Presenca.ID, &pc.Presenca.EstagiarioID, &pc.Presenca.Data,
			&pc.Presenca.HoraEntrada, &pc.Presenca.HoraSaida, &pc.Presenca.Observacao,
			&pc.Estagiario.ID, &pc.Estagiario.Nome, &pc.Estagiario.Email,
			&pc.Estagiario.Telefone, &pc.Estagiario.DataInicio, &pc.Estagiario.Ativo); err != nil {
			respondWithError(w, http.StatusInternalServerError, err.Error())
			return
		}
		presencas = append(presencas, pc)
	}

	respondWithJSON(w, http.StatusOK, presencas)
}

func (a *App) getPresenca(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id := vars["id"]

	var pc PresencaCompleta
	query := `
		SELECT p.id, p.estagiario_id, p.data, p.hora_entrada, p.hora_saida, p.observacao, 
               e.id, e.nome, e.email, e.telefone, e.data_inicio, e.ativo
		FROM presencas p
		JOIN estagiarios e ON p.estagiario_id = e.id
		WHERE p.id = ?
	`

	err := a.DB.QueryRow(query, id).Scan(
		&pc.Presenca.ID, &pc.Presenca.EstagiarioID, &pc.Presenca.Data,
		&pc.Presenca.HoraEntrada, &pc.Presenca.HoraSaida, &pc.Presenca.Observacao,
		&pc.Estagiario.ID, &pc.Estagiario.Nome, &pc.Estagiario.Email,
		&pc.Estagiario.Telefone, &pc.Estagiario.DataInicio, &pc.Estagiario.Ativo)

	if err != nil {
		if err == sql.ErrNoRows {
			respondWithError(w, http.StatusNotFound, "Registro de presença não encontrado")
		} else {
			respondWithError(w, http.StatusInternalServerError, err.Error())
		}
		return
	}

	respondWithJSON(w, http.StatusOK, pc)
}

func (a *App) registrarPresenca(w http.ResponseWriter, r *http.Request) {
	var p Presenca
	decoder := json.NewDecoder(r.Body)
	if err := decoder.Decode(&p); err != nil {
		respondWithError(w, http.StatusBadRequest, "Requisição inválida")
		return
	}
	defer r.Body.Close()

	// Verifica se o estagiário existe e está ativo
	var ativo bool
	err := a.DB.QueryRow("SELECT ativo FROM estagiarios WHERE id = ?", p.EstagiarioID).Scan(&ativo)
	if err != nil {
		if err == sql.ErrNoRows {
			respondWithError(w, http.StatusNotFound, "Estagiário não encontrado")
		} else {
			respondWithError(w, http.StatusInternalServerError, err.Error())
		}
		return
	}

	if !ativo {
		respondWithError(w, http.StatusBadRequest, "Estagiário não está ativo")
		return
	}

	// Formato correto das datas
	if p.Data == "" {
		p.Data = time.Now().Format("2006-01-02")
	}

	stmt, err := a.DB.Prepare("INSERT INTO presencas(estagiario_id, data, hora_entrada, hora_saida, observacao) VALUES(?, ?, ?, ?, ?)")
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}
	defer stmt.Close()

	res, err := stmt.Exec(p.EstagiarioID, p.Data, p.HoraEntrada, p.HoraSaida, p.Observacao)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}

	id, err := res.LastInsertId()
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}

	p.ID = int(id)
	respondWithJSON(w, http.StatusCreated, p)
}

func (a *App) updatePresenca(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id := vars["id"]

	var p Presenca
	decoder := json.NewDecoder(r.Body)
	if err := decoder.Decode(&p); err != nil {
		respondWithError(w, http.StatusBadRequest, "Requisição inválida")
		return
	}
	defer r.Body.Close()

	stmt, err := a.DB.Prepare("UPDATE presencas SET estagiario_id = ?, data = ?, hora_entrada = ?, hora_saida = ?, observacao = ? WHERE id = ?")
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}
	defer stmt.Close()

	_, err = stmt.Exec(p.EstagiarioID, p.Data, p.HoraEntrada, p.HoraSaida, p.Observacao, id)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}

	respondWithJSON(w, http.StatusOK, p)
}

func (a *App) deletePresenca(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id := vars["id"]

	stmt, err := a.DB.Prepare("DELETE FROM presencas WHERE id = ?")
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}
	defer stmt.Close()

	res, err := stmt.Exec(id)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}

	count, err := res.RowsAffected()
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}

	if count == 0 {
		respondWithError(w, http.StatusNotFound, "Registro de presença não encontrado")
		return
	}

	respondWithJSON(w, http.StatusOK, map[string]string{"result": "success"})
}

func (a *App) getPresencasByEstagiario(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	estagiarioId := vars["estagiarioId"]

	query := `
		SELECT p.id, p.estagiario_id, p.data, p.hora_entrada, p.hora_saida, p.observacao, 
               e.id, e.nome, e.email, e.telefone, e.data_inicio, e.ativo
		FROM presencas p
		JOIN estagiarios e ON p.estagiario_id = e.id
		WHERE p.estagiario_id = ?
		ORDER BY p.data DESC, p.hora_entrada DESC
	`

	rows, err := a.DB.Query(query, estagiarioId)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}
	defer rows.Close()

	presencas := []PresencaCompleta{}
	for rows.Next() {
		var pc PresencaCompleta
		if err := rows.Scan(
			&pc.Presenca.ID, &pc.Presenca.EstagiarioID, &pc.Presenca.Data,
			&pc.Presenca.HoraEntrada, &pc.Presenca.HoraSaida, &pc.Presenca.Observacao,
			&pc.Estagiario.ID, &pc.Estagiario.Nome, &pc.Estagiario.Email,
			&pc.Estagiario.Telefone, &pc.Estagiario.DataInicio, &pc.Estagiario.Ativo); err != nil {
			respondWithError(w, http.StatusInternalServerError, err.Error())
			return
		}
		presencas = append(presencas, pc)
	}

	respondWithJSON(w, http.StatusOK, presencas)
}

// Registrar entrada de estagiário
func (a *App) registrarEntrada(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	estagiarioId := vars["estagiarioId"]

	// Verificar se o estagiário existe e está ativo
	var ativo bool
	err := a.DB.QueryRow("SELECT ativo FROM estagiarios WHERE id = ?", estagiarioId).Scan(&ativo)
	if err != nil {
		if err == sql.ErrNoRows {
			respondWithError(w, http.StatusNotFound, "Estagiário não encontrado")
		} else {
			respondWithError(w, http.StatusInternalServerError, err.Error())
		}
		return
	}

	if !ativo {
		respondWithError(w, http.StatusBadRequest, "Estagiário não está ativo")
		return
	}

	// Verificar se já existe registro de entrada para hoje sem saída
	dataHoje := time.Now().Format("2006-01-02")
	var count int
	err = a.DB.QueryRow(`
		SELECT COUNT(*) FROM presencas 
		WHERE estagiario_id = ? AND data = ? AND hora_entrada IS NOT NULL AND hora_saida IS NULL
	`, estagiarioId, dataHoje).Scan(&count)

	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}

	if count > 0 {
		respondWithError(w, http.StatusBadRequest, "Estagiário já registrou entrada hoje e ainda não registrou saída")
		return
	}

	// Dados para o registro de presença
	horaAtual := time.Now().Format("15:04:05")
	var observacao string

	// Extrair observação da requisição se houver
	var reqBody map[string]string
	decoder := json.NewDecoder(r.Body)
	if err := decoder.Decode(&reqBody); err == nil {
		observacao = reqBody["observacao"]
	}
	defer r.Body.Close()

	// Inserir registro de entrada
	stmt, err := a.DB.Prepare("INSERT INTO presencas(estagiario_id, data, hora_entrada, observacao) VALUES(?, ?, ?, ?)")
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}
	defer stmt.Close()

	res, err := stmt.Exec(estagiarioId, dataHoje, horaAtual, observacao)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}

	id, err := res.LastInsertId()
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}

	// Retornar o registro criado
	respondWithJSON(w, http.StatusCreated, map[string]interface{}{
		"id":            id,
		"estagiario_id": estagiarioId,
		"data":          dataHoje,
		"hora_entrada":  horaAtual,
		"observacao":    observacao,
	})
}

// Registrar saída de estagiário
func (a *App) registrarSaida(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	estagiarioId := vars["estagiarioId"]

	// Verificar se o estagiário existe
	var ativo bool
	err := a.DB.QueryRow("SELECT ativo FROM estagiarios WHERE id = ?", estagiarioId).Scan(&ativo)
	if err != nil {
		if err == sql.ErrNoRows {
			respondWithError(w, http.StatusNotFound, "Estagiário não encontrado")
		} else {
			respondWithError(w, http.StatusInternalServerError, err.Error())
		}
		return
	}

	// Encontrar o registro de entrada mais recente sem saída
	dataHoje := time.Now().Format("2006-01-02")
	var presencaId int
	var horaEntrada string

	err = a.DB.QueryRow(`
		SELECT id, hora_entrada FROM presencas 
		WHERE estagiario_id = ? AND data = ? AND hora_entrada IS NOT NULL AND hora_saida IS NULL
		ORDER BY id DESC LIMIT 1
	`, estagiarioId, dataHoje).Scan(&presencaId, &horaEntrada)

	if err != nil {
		if err == sql.ErrNoRows {
			respondWithError(w, http.StatusNotFound, "Nenhum registro de entrada encontrado para hoje")
		} else {
			respondWithError(w, http.StatusInternalServerError, err.Error())
		}
		return
	}

	// Dados para o registro de saída
	horaSaida := time.Now().Format("15:04:05")

	// Extrair observação da requisição se houver
	var observacao string
	var reqBody map[string]string
	decoder := json.NewDecoder(r.Body)
	if err := decoder.Decode(&reqBody); err == nil {
		observacao = reqBody["observacao"]
	}
	defer r.Body.Close()

	// Atualizar o registro com a hora de saída
	stmt, err := a.DB.Prepare("UPDATE presencas SET hora_saida = ?, observacao = CONCAT(IFNULL(observacao, ''), ' ', ?) WHERE id = ?")
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}
	defer stmt.Close()

	_, err = stmt.Exec(horaSaida, observacao, presencaId)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}

	// Retornar o registro atualizado
	respondWithJSON(w, http.StatusOK, map[string]interface{}{
		"id":            presencaId,
		"estagiario_id": estagiarioId,
		"data":          dataHoje,
		"hora_entrada":  horaEntrada,
		"hora_saida":    horaSaida,
		"observacao":    observacao,
	})
}

// Função para gerar relatório mensal de presenças
func (a *App) getRelatorioMensal(w http.ResponseWriter, r *http.Request) {
	// Obter parâmetros de consulta para mês e ano
	queryValues := r.URL.Query()

	// Obter mês e ano da query ou usar o mês atual
	var mes, ano int
	var err error

	agora := time.Now()

	ano = agora.Year()

	// Substituir pelos valores da query se informados
	mesStr := queryValues.Get("mes")
	anoStr := queryValues.Get("ano")

	if mesStr != "" {
		mes, err = parseInt(mesStr)
		if err != nil || mes < 1 || mes > 12 {
			respondWithError(w, http.StatusBadRequest, "Mês inválido. Deve ser um número entre 1 e 12")
			return
		}
	}

	if anoStr != "" {
		ano, err = parseInt(anoStr)
		if err != nil || ano < 2000 || ano > 2100 {
			respondWithError(w, http.StatusBadRequest, "Ano inválido")
			return
		}
	}

	// Consulta SQL para relatório mensal
	query := `
		SELECT 
			e.id, 
			e.nome, 
			? AS mes, 
			? AS ano, 
			COUNT(p.id) AS total_presencas,
			SUM(
				CASE
					WHEN p.hora_saida IS NOT NULL THEN 
						TIME_TO_SEC(TIMEDIFF(p.hora_saida, p.hora_entrada)) / 3600
					ELSE 0
				END
			) AS total_horas
		FROM 
			estagiarios e
		LEFT JOIN 
			presencas p ON e.id = p.estagiario_id AND MONTH(p.data) = ? AND YEAR(p.data) = ?
		WHERE 
			e.ativo = true
		GROUP BY 
			e.id, e.nome
		ORDER BY 
			e.nome
	`

	rows, err := a.DB.Query(query, mes, ano, mes, ano)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}
	defer rows.Close()

	relatorios := []RelatorioMensal{}
	for rows.Next() {
		var r RelatorioMensal
		if err := rows.Scan(&r.EstagiarioID, &r.NomeEstagiario, &r.Mes, &r.Ano, &r.TotalPresencas, &r.TotalHoras); err != nil {
			respondWithError(w, http.StatusInternalServerError, err.Error())
			return
		}
		relatorios = append(relatorios, r)
	}

	respondWithJSON(w, http.StatusOK, relatorios)
}

// Helper para converter string para int
func parseInt(s string) (int, error) {
	var i int
	_, err := fmt.Sscanf(s, "%d", &i)
	return i, err
}

// Helper para responder com JSON
func respondWithJSON(w http.ResponseWriter, code int, payload interface{}) {
	response, _ := json.Marshal(payload)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	w.Write(response)
}

// Helper para responder com erro
func respondWithError(w http.ResponseWriter, code int, message string) {
	respondWithJSON(w, code, map[string]string{"error": message})
}

func main() {
	a := App{}
	a.Initialize()
	port := getEnv("PORT", "8080")
	a.Run(":" + port)
}
