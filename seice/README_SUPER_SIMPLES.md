# 🚀 SISTEMA SUPER SIMPLES DE PRESENÇAS v2.0

## 🎯 NOVIDADES v2.0

**AGORA PROCESSA APENAS LOGS NOVOS!** 🔥

- ✅ **Detecta logs novos automaticamente**
- ✅ **Evita reprocessar logs antigos**
- ✅ **Identifica ENTRADA/SAÍDA corretamente**
- ✅ **Calcula horas trabalhadas**
- ✅ **Logs detalhados de cada ação**

## O QUE FAZ

**SIMPLES**: Coleta apenas logs NOVOS do Control ID e registra presenças automaticamente! 🎉

## COMO USAR

### ✨ Modo Automático (Recomendado)
```bash
cd seice
python manage.py runserver
# O sistema inicia SOZINHO em 3 segundos! 🚀
```

### 🔍 Verificar se está funcionando
```bash
python manage.py presencas_simples status
```

### 🔄 Coleta manual (teste)
```bash
python manage.py presencas_simples manual
```

### � Reset de controle (para testes)
```bash
python manage.py presencas_simples reset
```

### 📱 Teste de logs novos
```bash
python teste_logs_novos.py
```

## 🎯 FLUXO v2.0

1. **🔄 A cada 30 segundos**: Busca TODOS os logs do Control ID
2. **� Filtra logs novos**: Compara com último processado
3. **�👤 Identifica estagiários**: Pelo `control_id_user_id`
4. **📝 Processa cada log novo**:
   - **📥 ENTRADA**: Eventos `in`, `entrada`, `face_in`, `entry`, `1`, `access_granted`
   - **📤 SAÍDA**: Eventos `out`, `saida`, `face_out`, `exit`, `0`, `access_denied`
5. **⏱️ Calcula horas**: Para saídas (entrada → saída)
6. **💾 Salva no banco**: Tabela `Presenca` automaticamente
7. **📊 Atualiza controle**: Marca último log processado

## 🔍 DETECÇÃO DE LOGS NOVOS

O sistema mantém controle do **último log processado**:
- **Timestamp**: Data/hora do último log
- **Log ID**: Identificador único
- **Total processados**: Contador geral

A cada execução:
1. Compara timestamp de cada log
2. Processa apenas os **mais recentes**
3. Atualiza controle automaticamente

## APIS SIMPLES v2.0

```bash
# Status (mostra último processamento)
GET /api/presencas-auto/status/

# Coleta manual (processa apenas logs novos)
POST /api/presencas-auto/manual/

# Controlar
POST /api/presencas-auto/controle/
{"action": "start"}   # Iniciar
{"action": "stop"}    # Parar  
{"action": "reset"}   # Resetar controle (para testes)
```

## CONFIGURAÇÃO

- **IP Control ID**: `192.168.3.40:81`
- **Usuário**: `admin` / **Senha**: `admin`
- **Intervalo**: `30 segundos`
- **Auto-start**: `✅ SIM` (inicia sozinho)

## REQUISITOS

1. **Estagiários devem ter `control_id_user_id`** preenchido
2. **Control ID acessível** na rede
3. **Servidor Django rodando**

## PRONTO! 🎉 v2.0

Agora é só:
1. **Ligar o servidor Django**
2. **Deixar rodando**
3. **Apenas logs NOVOS são processados!**
4. **Presenças registradas automaticamente!**
5. **Sem reprocessamento desnecessário!**

### 🎯 VANTAGENS v2.0:
- ⚡ **Mais eficiente** (só logs novos)
- 🎯 **Mais preciso** (identifica entrada/saída)
- 📊 **Mais informativo** (logs detalhados)
- 🚫 **Sem duplicação** (evita reprocessamento)

É isso! **SUPER SIMPLES e EFICIENTE!** 🚀
