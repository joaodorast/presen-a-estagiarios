
CREATE DATABASE IF NOT EXISTS seice CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;


USE seice;

CREATE TABLE IF NOT EXISTS admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS estagiarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    data_inicio DATE NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS presencas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    estagiario_id INT NOT NULL,
    data DATE NOT NULL,
    entrada TIME NOT NULL,
    saida TIME NULL,
    horas VARCHAR(10) NULL,
    observacao TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (estagiario_id) REFERENCES estagiarios(id)
);


CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    admin BOOLEAN NOT NULL DEFAULT FALSE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acesso TIMESTAMP NULL
);


CREATE TABLE IF NOT EXISTS configuracoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_empresa VARCHAR(100) NOT NULL,
    logo_url VARCHAR(255) NULL,
    hora_entrada_padrao TIME DEFAULT '08:00:00',
    hora_saida_padrao TIME DEFAULT '17:00:00',
    tolerancia_atraso INT DEFAULT 15,
    email_notificacao VARCHAR(100) NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS feriados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data DATE NOT NULL UNIQUE,
    descricao VARCHAR(100) NOT NULL
);


CREATE INDEX idx_estagiarios_ativo ON estagiarios(ativo);
CREATE INDEX idx_presencas_data ON presencas(data);
CREATE INDEX idx_presencas_estagiario_data ON presencas(estagiario_id, data);


DELIMITER //
CREATE PROCEDURE calcular_horas(IN p_entrada TIME, IN p_saida TIME, OUT p_horas VARCHAR(10))
BEGIN
    DECLARE horas INT;
    DECLARE minutos INT;
    
    SET horas = TIMESTAMPDIFF(HOUR, p_entrada, p_saida);
    SET minutos = TIMESTAMPDIFF(MINUTE, p_entrada, p_saida) % 60;
    
    SET p_horas = CONCAT(horas, ':', LPAD(minutos, 2, '0'));
END //
DELIMITER ;


DELIMITER //
CREATE TRIGGER before_presencas_insert_update
BEFORE INSERT ON presencas
FOR EACH ROW
BEGIN
    IF NEW.saida IS NOT NULL AND NEW.entrada IS NOT NULL THEN
        CALL calcular_horas(NEW.entrada, NEW.saida, @horas);
        SET NEW.horas = @horas;
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER before_presencas_update
BEFORE UPDATE ON presencas
FOR EACH ROW
BEGIN
    IF NEW.saida IS NOT NULL AND NEW.entrada IS NOT NULL THEN
        CALL calcular_horas(NEW.entrada, NEW.saida, @horas);
        SET NEW.horas = @horas;
    END IF;
END //
DELIMITER ;


CREATE OR REPLACE VIEW vw_presencas AS
SELECT 
    p.id,
    p.estagiario_id,
    e.nome AS nome_estagiario,
    p.data,
    p.entrada,
    p.saida,
    p.horas,
    p.observacao
FROM presencas p
JOIN estagiarios e ON p.estagiario_id = e.id;


CREATE OR REPLACE VIEW vw_estatisticas_estagiarios AS
SELECT 
    e.id,
    e.nome,
    COUNT(p.id) AS total_presencas,
    SEC_TO_TIME(SUM(TIME_TO_SEC(p.horas))) AS total_horas,
    SEC_TO_TIME(AVG(TIME_TO_SEC(p.horas))) AS media_diaria
FROM estagiarios e
LEFT JOIN presencas p ON e.id = p.estagiario_id AND p.saida IS NOT NULL
WHERE e.ativo = TRUE
GROUP BY e.id;


INSERT INTO estagiarios (nome, email, telefone, data_inicio, ativo) VALUES
('João Pedro', 'joaopedro@gmail.com', '(21) 98765-4321', '2024-02-15', true),
('Maria Clara', 'mariaclara@gmail.com', '(21) 91234-5678', '2024-03-01', true),
('Miguel Combas', 'miguelcombas@gmail.com', '(21) 99876-5432', '2023-11-10', true),
('Eloá Christine', 'eloacristine@gmail.com', '(21) 95555-4444', '2024-01-20', false),
('Pedro Henricky', 'pedrohenricky@gmail.com', '(21) 93333-2222', '2023-10-05', true);


INSERT INTO usuarios (nome, email, senha, admin) VALUES
('Administrador', 'admin@seice.com', '$2a$10$qJKh5.5UjbS3vVxTKLZzWOsb8qU5YYpyXU1dKm.9z1Wa5X5fHkbUu', true); -- Senha: admin123


INSERT INTO configuracoes (nome_empresa, hora_entrada_padrao, hora_saida_padrao, tolerancia_atraso) VALUES
('Colégio Seice', '14:00:00', '17:30:00', 15);



INSERT INTO presencas (estagiario_id, data, entrada, saida, observacao) VALUES
-- João Pedro
(1, DATE_SUB(CURDATE(), INTERVAL 5 DAY), '08:05:00', '17:10:00', 'Dia normal'),
(1, DATE_SUB(CURDATE(), INTERVAL 4 DAY), '08:00:00', '17:00:00', 'Dia normal'),
(1, DATE_SUB(CURDATE(), INTERVAL 3 DAY), '08:10:00', '17:05:00', 'Pequeno atraso'),
(1, DATE_SUB(CURDATE(), INTERVAL 2 DAY), '08:05:00', '17:15:00', 'Dia normal'),
(1, DATE_SUB(CURDATE(), INTERVAL 1 DAY), '08:00:00', '17:00:00', 'Dia normal'),

-- Maria Clara
(2, DATE_SUB(CURDATE(), INTERVAL 5 DAY), '08:30:00', '17:30:00', 'Dia normal'),
(2, DATE_SUB(CURDATE(), INTERVAL 4 DAY), '08:25:00', '17:25:00', 'Dia normal'),
(2, DATE_SUB(CURDATE(), INTERVAL 3 DAY), '08:30:00', '17:30:00', 'Dia normal'),
(2, DATE_SUB(CURDATE(), INTERVAL 2 DAY), '08:40:00', '17:40:00', 'Pequeno atraso'),
(2, DATE_SUB(CURDATE(), INTERVAL 1 DAY), '08:30:00', '17:30:00', 'Dia normal'),

-- Miguel Combas
(3, DATE_SUB(CURDATE(), INTERVAL 5 DAY), '08:15:00', '17:00:00', 'Dia normal'),
(3, DATE_SUB(CURDATE(), INTERVAL 4 DAY), '08:15:00', '17:15:00', 'Dia normal'),
(3, DATE_SUB(CURDATE(), INTERVAL 3 DAY), '08:20:00', '17:15:00', 'Dia normal'),
(3, DATE_SUB(CURDATE(), INTERVAL 2 DAY), '08:10:00', '17:00:00', 'Dia normal'),
(3, DATE_SUB(CURDATE(), INTERVAL 1 DAY), '08:15:00', '17:00:00', 'Dia normal'),

-- Pedro Henricky
(5, DATE_SUB(CURDATE(), INTERVAL 5 DAY), '09:00:00', '18:00:00', 'Horário alternativo'),
(5, DATE_SUB(CURDATE(), INTERVAL 4 DAY), '09:00:00', '18:00:00', 'Horário alternativo'),
(5, DATE_SUB(CURDATE(), INTERVAL 3 DAY), '08:45:00', '17:50:00', 'Dia normal'),
(5, DATE_SUB(CURDATE(), INTERVAL 2 DAY), '09:00:00', '18:00:00', 'Horário alternativo'),
(5, DATE_SUB(CURDATE(), INTERVAL 1 DAY), '08:50:00', '18:05:00', 'Horário alternativo'),

-- Entrada hoje para alguns estagiários (sem saída ainda)
(1, CURDATE(), '08:00:00', NULL, 'Entrada normal'),
(2, CURDATE(), '08:35:00', NULL, 'Pequeno atraso'),
(3, CURDATE(), '08:15:00', NULL, 'Entrada normal');

-
DELIMITER //
CREATE FUNCTION dias_uteis(data_inicio DATE, data_fim DATE) RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE dias INT DEFAULT 0;
    DECLARE data_atual DATE;
    
    SET data_atual = data_inicio;
    
    WHILE data_atual <= data_fim DO
       
        IF DAYOFWEEK(data_atual) NOT IN (1, 7) THEN
           
            IF NOT EXISTS (SELECT 1 FROM feriados WHERE data = data_atual) THEN
                SET dias = dias + 1;
            END IF;
        END IF;
        
        SET data_atual = DATE_ADD(data_atual, INTERVAL 1 DAY);
    END WHILE;
    
    RETURN dias;
END //
DELIMITER ;


DELIMITER //
CREATE PROCEDURE relatorio_mensal(IN p_mes INT, IN p_ano INT)
BEGIN
    DECLARE data_inicio DATE;
    DECLARE data_fim DATE;
    
    SET data_inicio = CONCAT(p_ano, '-', LPAD(p_mes, 2, '0'), '-01');
    SET data_fim = LAST_DAY(data_inicio);
    
    SELECT 
        e.id,
        e.nome,
        COUNT(p.id) AS dias_presentes,
        dias_uteis(data_inicio, data_fim) AS dias_uteis,
        SEC_TO_TIME(SUM(TIME_TO_SEC(p.horas))) AS total_horas,
        SEC_TO_TIME(AVG(TIME_TO_SEC(p.horas))) AS media_diaria
    FROM estagiarios e
    LEFT JOIN presencas p ON e.id = p.estagiario_id 
                          AND p.data BETWEEN data_inicio AND data_fim
                          AND p.saida IS NOT NULL
    WHERE e.ativo = TRUE
    GROUP BY e.id;
END //
DELIMITER ;