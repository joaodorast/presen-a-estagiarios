    // Sistema de Controle de Estagiários (SEICE)
// Versão 1.0.0

// Mock data para simulação do sistema
let estagiarios = [
    { id: 1, nome: "João Silva", email: "joao.silva@email.com", telefone: "(11) 98765-4321", dataInicio: "2024-02-15", ativo: true },
    { id: 2, nome: "Maria Oliveira", email: "maria.oliveira@email.com", telefone: "(11) 91234-5678", dataInicio: "2024-03-01", ativo: true },
    { id: 3, nome: "Lucas Santos", email: "lucas.santos@email.com", telefone: "(11) 99876-5432", dataInicio: "2023-11-10", ativo: true },
    { id: 4, nome: "Amanda Costa", email: "amanda.costa@email.com", telefone: "(11) 95555-4444", dataInicio: "2024-01-20", ativo: false },
    { id: 5, nome: "Pedro Almeida", email: "pedro.almeida@email.com", telefone: "(11) 93333-2222", dataInicio: "2023-10-05", ativo: true }
];

let presencas = [
    { id: 1, estagiarioId: 1, data: "2024-05-19", entrada: "08:05:00", saida: "17:15:00", horas: "9:10", observacao: "" },
    { id: 2, estagiarioId: 2, data: "2024-05-19", entrada: "08:30:00", saida: "17:30:00", horas: "9:00", observacao: "" },
    { id: 3, estagiarioId: 3, data: "2024-05-19", entrada: "08:15:00", saida: "17:00:00", horas: "8:45", observacao: "" },
    { id: 4, estagiarioId: 1, data: "2024-05-18", entrada: "08:00:00", saida: "17:00:00", horas: "9:00", observacao: "" },
    { id: 5, estagiarioId: 2, data: "2024-05-18", entrada: "08:30:00", saida: "17:30:00", horas: "9:00", observacao: "" },
    { id: 6, estagiarioId: 5, data: "2024-05-18", entrada: "09:00:00", saida: "18:00:00", horas: "9:00", observacao: "" },
    { id: 7, estagiarioId: 1, data: "2024-05-17", entrada: "08:10:00", saida: "17:05:00", horas: "8:55", observacao: "" },
    { id: 8, estagiarioId: 3, data: "2024-05-17", entrada: "08:20:00", saida: "17:15:00", horas: "8:55", observacao: "" },
    { id: 9, estagiarioId: 5, data: "2024-05-17", entrada: "08:45:00", saida: "17:50:00", horas: "9:05", observacao: "" }
];

// Array para presenças de hoje (será preenchido durante a inicialização)
let presencasHoje = [];

// Data atual
const hoje = new Date();
const dataAtual = hoje.toISOString().split('T')[0];
const dataHojeFormatada = formatarData(dataAtual);

// Elemento DOM para a data atual
const dataHojeEl = document.getElementById('today-date');
dataHojeEl.textContent = dataHojeFormatada;

// Navegação entre páginas
const navItems = document.querySelectorAll('.sidebar nav ul li');
const pages = document.querySelectorAll('.page');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    initMenuToggle();
    initModals();
    initTodayPresences();
    loadDashboardStats();
    loadEstagiarios();
    loadPresencasTable();
    initEventListeners();
    setReportDefaultDate();
});

// Inicializa a navegação
function initNavigation() {
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            // Remove active class from all nav items
            navItems.forEach(navItem => navItem.classList.remove('active'));
            
            // Add active class to clicked item
            this.classList.add('active');
            
            // Get page id from data attribute
            const pageId = this.getAttribute('data-page');
            
            // Hide all pages
            pages.forEach(page => page.classList.remove('active'));
            
            // Show selected page
            document.getElementById(pageId).classList.add('active');
        });
    });
}

// Inicializa o toggle do menu lateral
function initMenuToggle() {
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    menuToggle.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
        mainContent.classList.toggle('expanded');
    });
}

// Inicializa os modais
function initModals() {
    // Get all modals
    const modals = document.querySelectorAll('.modal');
    
    // Get all elements that close modals
    const closeBtns = document.querySelectorAll('.close, .modal-cancel');
    
    // When the user clicks the button, open the modal
    document.getElementById('btn-registrar-entrada').addEventListener('click', function() {
        openModal('modal-registrar-entrada');
        loadEstagiarioSelect('entrada-estagiario', true);
    });
    
    document.getElementById('btn-registrar-saida').addEventListener('click', function() {
        openModal('modal-registrar-saida');
        loadEstagiarioSelectWithPresence('saida-estagiario');
    });
    
    document.getElementById('btn-novo-estagiario').addEventListener('click', function() {
        document.getElementById('modal-estagiario-titulo').textContent = 'Novo Estagiário';
        document.getElementById('estagiario-id').value = '';
        document.getElementById('estagiario-nome').value = '';
        document.getElementById('estagiario-email').value = '';
        document.getElementById('estagiario-telefone').value = '';
        document.getElementById('estagiario-data-inicio').value = dataAtual;
        document.getElementById('estagiario-ativo').value = 'true';
        openModal('modal-estagiario');
    });
    
    // When the user clicks on <span> (x) or cancel button, close the modal
    closeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            modals.forEach(modal => {
                modal.classList.remove('active');
            });
        });
    });
    
    // When the user clicks anywhere outside of the modal, close it
    window.addEventListener('click', function(event) {
        modals.forEach(modal => {
            if (event.target == modal) {
                modal.classList.remove('active');
            }
        });
    });
}

// Função para abrir um modal específico
function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

// Inicializa as presenças de hoje
function initTodayPresences() {
    // Filter presences for today
    presencasHoje = presencas.filter(p => p.data === dataAtual);
    
    // Load today's presences table
    loadTodayPresencesTable();
}

// Carrega estatísticas do dashboard
function loadDashboardStats() {
    // Total de estagiários
    document.getElementById('total-estagiarios').textContent = estagiarios.filter(e => e.ativo).length;
    
    // Presentes hoje
    document.getElementById('presentes-hoje').textContent = presencasHoje.length;
    
    // Presenças do mês
    const mesAtual = hoje.getMonth() + 1;
    const anoAtual = hoje.getFullYear();
    const presencasMes = presencas.filter(p => {
        const presencaData = new Date(p.data);
        return presencaData.getMonth() + 1 === mesAtual && presencaData.getFullYear() === anoAtual;
    });
    document.getElementById('presencas-mes').textContent = presencasMes.length;
    
    // Horas totais do mês
    let horasTotais = 0;
    presencasMes.forEach(p => {
        const [horas, minutos] = p.horas.split(':').map(Number);
        horasTotais += horas + (minutos / 60);
    });
    document.getElementById('horas-mes').textContent = horasTotais.toFixed(1) + 'h';
}

// Carrega a tabela de presenças de hoje
function loadTodayPresencesTable() {
    const tableBody = document.querySelector('#presencas-hoje-tabela tbody');
    tableBody.innerHTML = '';
    
    if (presencasHoje.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `<td colspan="4" class="text-center">Nenhuma presença registrada hoje.</td>`;
        tableBody.appendChild(row);
        return;
    }
    
    presencasHoje.forEach(presenca => {
        const estagiario = estagiarios.find(e => e.id === presenca.estagiarioId);
        if (!estagiario) return;
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${estagiario.nome}</td>
            <td>${presenca.entrada}</td>
            <td>${presenca.saida || '---'}</td>
            <td>
                <span class="badge ${presenca.saida ? 'inactive' : 'active'}">
                    ${presenca.saida ? 'Finalizado' : 'Em andamento'}
                </span>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

// Carrega a tabela de estagiários
function loadEstagiarios() {
    const tableBody = document.querySelector('#estagiarios-tabela tbody');
    tableBody.innerHTML = '';
    
    estagiarios.forEach(estagiario => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${estagiario.id}</td>
            <td>${estagiario.nome}</td>
            <td>${estagiario.email}</td>
            <td>${estagiario.telefone}</td>
            <td>${formatarData(estagiario.dataInicio)}</td>
            <td>
                <span class="badge ${estagiario.ativo ? 'active' : 'inactive'}">
                    ${estagiario.ativo ? 'Ativo' : 'Inativo'}
                </span>
            </td>
            <td>
                <div class="actions-column">
                    <button class="btn-icon edit" data-id="${estagiario.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon delete" data-id="${estagiario.id}">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
            </td>
        `;
        tableBody.appendChild(row);
    });
    
    // Adiciona eventos aos botões de edição
    document.querySelectorAll('.btn-icon.edit').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = parseInt(this.getAttribute('data-id'));
            editEstagiario(id);
        });
    });
    
    // Adiciona eventos aos botões de exclusão
    document.querySelectorAll('.btn-icon.delete').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = parseInt(this.getAttribute('data-id'));
            if (confirm('Tem certeza que deseja excluir este estagiário?')) {
                deleteEstagiario(id);
            }
        });
    });
}

// Carrega a tabela de presenças
function loadPresencasTable(filteredPresencas = null) {
    const tableBody = document.querySelector('#presencas-tabela tbody');
    tableBody.innerHTML = '';
    
    const presencasToShow = filteredPresencas || presencas;
    
    if (presencasToShow.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `<td colspan="8" class="text-center">Nenhuma presença encontrada.</td>`;
        tableBody.appendChild(row);
        return;
    }
    
    presencasToShow.forEach(presenca => {
        const estagiario = estagiarios.find(e => e.id === presenca.estagiarioId);
        if (!estagiario) return;
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${presenca.id}</td>
            <td>${estagiario.nome}</td>
            <td>${formatarData(presenca.data)}</td>
            <td>${presenca.entrada}</td>
            <td>${presenca.saida || '---'}</td>
            <td>${presenca.horas || '---'}</td>
            <td>${presenca.observacao || '---'}</td>
            <td>
                <div class="actions-column">
                    <button class="btn-icon edit" data-id="${presenca.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon delete" data-id="${presenca.id}">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
            </td>
        `;
        tableBody.appendChild(row);
    });
    
    // Adicionar eventos para edição e exclusão
    // (Implementação semelhante à loadEstagiarios)
}

// Carrega o select de estagiários
function loadEstagiarioSelect(selectId, onlyActive = false) {
    const select = document.getElementById(selectId);
    select.innerHTML = '<option value="">Selecione o estagiário</option>';
    
    const filteredEstagiarios = onlyActive ? estagiarios.filter(e => e.ativo) : estagiarios;
    
    filteredEstagiarios.forEach(estagiario => {
        const option = document.createElement('option');
        option.value = estagiario.id;
        option.textContent = estagiario.nome;
        select.appendChild(option);
    });
}

// Carrega select de estagiários que entraram hoje mas não saíram
function loadEstagiarioSelectWithPresence(selectId) {
    const select = document.getElementById(selectId);
    select.innerHTML = '<option value="">Selecione o estagiário</option>';
    
    // Filtra estagiários que entraram hoje mas não saíram
    const estagiariosPresentesHoje = presencasHoje
        .filter(p => !p.saida)
        .map(p => p.estagiarioId);
    
    estagiarios
        .filter(e => e.ativo && estagiariosPresentesHoje.includes(e.id))
        .forEach(estagiario => {
            const option = document.createElement('option');
            option.value = estagiario.id;
            option.textContent = estagiario.nome;
            select.appendChild(option);
        });
}

// Carrega o filtro de estagiários na página de presenças
function loadEstagiarioFilter() {
    const select = document.getElementById('filtro-estagiario');
    select.innerHTML = '<option value="">Todos</option>';
    
    estagiarios.forEach(estagiario => {
        const option = document.createElement('option');
        option.value = estagiario.id;
        option.textContent = estagiario.nome;
        select.appendChild(option);
    });
}

// Inicializa todos os listeners de eventos
function initEventListeners() {
    // Botão para confirmar entrada
    document.getElementById('btn-confirmar-entrada').addEventListener('click', registrarEntrada);
    
    // Botão para confirmar saída
    document.getElementById('btn-confirmar-saida').addEventListener('click', registrarSaida);
    
    // Botão para salvar estagiário
    document.getElementById('btn-salvar-estagiario').addEventListener('click', salvarEstagiario);
    
    // Botão para filtrar presenças
    document.getElementById('btn-filtrar-presencas').addEventListener('click', filtrarPresencas);
    
    // Botão para gerar relatório
    document.getElementById('btn-gerar-relatorio').addEventListener('click', gerarRelatorio);
    
    // Botão para exportar relatório
    document.getElementById('btn-exportar-relatorio').addEventListener('click', exportarRelatorio);
    
    // Campo de busca de estagiários
    document.getElementById('search-estagiario').addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        
        if (searchTerm.length < 2) {
            loadEstagiarios();
            return;
        }
        
        const filteredEstagiarios = estagiarios.filter(estagiario => 
            estagiario.nome.toLowerCase().includes(searchTerm) || 
            estagiario.email.toLowerCase().includes(searchTerm)
        );
        
        const tableBody = document.querySelector('#estagiarios-tabela tbody');
        tableBody.innerHTML = '';
        
        if (filteredEstagiarios.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = `<td colspan="7" class="text-center">Nenhum estagiário encontrado.</td>`;
            tableBody.appendChild(row);
            return;
        }
        
        // Carrega os estagiários filtrados (código similar ao loadEstagiarios)
        // Implementação omitida para brevidade
    });
    
    // Carregar filtro de estagiários quando a página de presenças for aberta
    document.querySelector('[data-page="presencas"]').addEventListener('click', function() {
        loadEstagiarioFilter();
        // Definir datas padrão para filtro (último mês)
        const today = new Date();
        const lastMonth = new Date();
        lastMonth.setMonth(today.getMonth() - 1);
        
        document.getElementById('filtro-data-fim').value = today.toISOString().split('T')[0];
        document.getElementById('filtro-data-inicio').value = lastMonth.toISOString().split('T')[0];
    });
}

// Função para registrar entrada
function registrarEntrada() {
    const estagiarioId = parseInt(document.getElementById('entrada-estagiario').value);
    const observacao = document.getElementById('entrada-observacao').value;
    
    if (!estagiarioId) {
        showToast('Por favor, selecione um estagiário', 'error');
        return;
    }
    
    // Verifica se o estagiário já tem entrada hoje
    const jaTemEntrada = presencasHoje.some(p => p.estagiarioId === estagiarioId);
    if (jaTemEntrada) {
        showToast('Este estagiário já registrou entrada hoje', 'error');
        return;
    }
    
    // Registra nova entrada
    const horaAtual = new Date().toTimeString().split(' ')[0];
    const novaPresenca = {
        id: presencas.length + 1,
        estagiarioId: estagiarioId,
        data: dataAtual,
        entrada: horaAtual,
        saida: null,
        horas: null,
        observacao: observacao
    };
    
    presencas.push(novaPresenca);
    presencasHoje.push(novaPresenca);
    
    // Atualiza UI
    loadTodayPresencesTable();
    loadDashboardStats();
    
    // Fecha modal e mostra confirmação
    document.getElementById('modal-registrar-entrada').classList.remove('active');
    document.getElementById('entrada-estagiario').value = '';
    document.getElementById('entrada-observacao').value = '';
    
    showToast('Entrada registrada com sucesso!', 'success');
}

// Função para registrar saída
function registrarSaida() {
    const estagiarioId = parseInt(document.getElementById('saida-estagiario').value);
    const observacao = document.getElementById('saida-observacao').value;
    
    if (!estagiarioId) {
        showToast('Por favor, selecione um estagiário', 'error');
        return;
    }
    
    // Encontra a presença para atualizar
    const presencaIndex = presencasHoje.findIndex(p => p.estagiarioId === estagiarioId && !p.saida);
    
    if (presencaIndex === -1) {
        showToast('Não foi encontrada entrada aberta para este estagiário', 'error');
        return;
    }
    
    // Registra saída
    const horaAtual = new Date().toTimeString().split(' ')[0];
    const horaEntrada = presencasHoje[presencaIndex].entrada;
    const horas = calcularHoras(horaEntrada, horaAtual);
    
    presencasHoje[presencaIndex].saida = horaAtual;
    presencasHoje[presencaIndex].horas = horas;
    
    if (observacao) {
        presencasHoje[presencaIndex].observacao = observacao;
    }
    
    // Atualiza também no array principal de presenças
    const presencaGlobalIndex = presencas.findIndex(p => p.id === presencasHoje[presencaIndex].id);
    if (presencaGlobalIndex !== -1) {
        presencas[presencaGlobalIndex] = { ...presencasHoje[presencaIndex] };
    }
    
    // Atualiza UI
    loadTodayPresencesTable();
    loadDashboardStats();
    
    // Fecha modal e mostra confirmação
    document.getElementById('modal-registrar-saida').classList.remove('active');
    document.getElementById('saida-estagiario').value = '';
    document.getElementById('saida-observacao').value = '';
    
    showToast('Saída registrada com sucesso!', 'success');
}

// Editar estagiário
function editEstagiario(id) {
    const estagiario = estagiarios.find(e => e.id === id);
    if (!estagiario) return;
    
    document.getElementById('modal-estagiario-titulo').textContent = 'Editar Estagiário';
    document.getElementById('estagiario-id').value = estagiario.id;
    document.getElementById('estagiario-nome').value = estagiario.nome;
    document.getElementById('estagiario-email').value = estagiario.email;
    document.getElementById('estagiario-telefone').value = estagiario.telefone;
    document.getElementById('estagiario-data-inicio').value = estagiario.dataInicio;
    document.getElementById('estagiario-ativo').value = estagiario.ativo.toString();
    
    openModal('modal-estagiario');
}

// Salvar estagiário (novo ou editado)
function salvarEstagiario() {
    const id = document.getElementById('estagiario-id').value;
    const nome = document.getElementById('estagiario-nome').value;
    const email = document.getElementById('estagiario-email').value;
    const telefone = document.getElementById('estagiario-telefone').value;
    const dataInicio = document.getElementById('estagiario-data-inicio').value;
    const ativo = document.getElementById('estagiario-ativo').value === 'true';
    
    if (!nome || !email || !telefone || !dataInicio) {
        showToast('Por favor, preencha todos os campos obrigatórios', 'error');
        return;
    }
    
    if (id) {
        // Editar estagiário existente
        const index = estagiarios.findIndex(e => e.id === parseInt(id));
        if (index !== -1) {
            estagiarios[index] = {
                id: parseInt(id),
                nome,
                email,
                telefone,
                dataInicio,
                ativo
            };
            showToast('Estagiário atualizado com sucesso!', 'success');
        }
    } else {
        // Novo estagiário
        const novoId = estagiarios.length > 0 ? Math.max(...estagiarios.map(e => e.id)) + 1 : 1;
        estagiarios.push({
            id: novoId,
            nome,
            email,
            telefone,
            dataInicio,
            ativo
        });
        showToast('Estagiário cadastrado com sucesso!', 'success');
    }
    
    // Fecha modal e atualiza tabela
    document.getElementById('modal-estagiario').classList.remove('active');
    loadEstagiarios();
    loadDashboardStats();
}

// Excluir estagiário
function deleteEstagiario(id) {
    // Verifica se há presenças associadas
    const temPresencas = presencas.some(p => p.estagiarioId === id);
    
    if (temPresencas) {
        showToast('Não é possível excluir este estagiário pois há presenças registradas', 'error');
        return;
    }
    
    const index = estagiarios.findIndex(e => e.id === id);
    if (index !== -1) {
        estagiarios.splice(index, 1);
        loadEstagiarios();
        loadDashboardStats();
        showToast('Estagiário excluído com sucesso!', 'success');
    }
}

// Filtrar presenças
function filtrarPresencas() {
    const estagiarioId = document.getElementById('filtro-estagiario').value;
    const dataInicio = document.getElementById('filtro-data-inicio').value;
    const dataFim = document.getElementById('filtro-data-fim').value;
    
    let filtered = [...presencas];
    
    if (estagiarioId) {
        filtered = filtered.filter(p => p.estagiarioId === parseInt(estagiarioId));
    }
    
    if (dataInicio) {
        filtered = filtered.filter(p => p.data >= dataInicio);
    }
    
    if (dataFim) {
        filtered = filtered.filter(p => p.data <= dataFim);
    }
    
    loadPresencasTable(filtered);
}

// Gerar relatório
function gerarRelatorio() {
    const mes = parseInt(document.getElementById('relatorio-mes').value);
    const ano = parseInt(document.getElementById('relatorio-ano').value);
    
    if (!mes || !ano) {
        showToast('Por favor, selecione o mês e o ano', 'error');
        return;
    }
    
    // Filtra presenças do mês e ano selecionados
    const presencasFiltradas = presencas.filter(p => {
        const presencaData = new Date(p.data);
        return presencaData.getMonth() + 1 === mes && presencaData.getFullYear() === ano;
    });
    
    if (presencasFiltradas.length === 0) {
        showToast('Não há dados para o período selecionado', 'warning');
        return;
    }
    
    // Calcula estatísticas
    const totalPresencas = presencasFiltradas.length;
    
    let totalHoras = 0;
    presencasFiltradas.forEach(p => {
        if (p.horas) {
            const [horas, minutos] = p.horas.split(':').map(Number);
            totalHoras += horas + (minutos / 60);
        }
    });
    
    const mediaHoras = totalHoras / totalPresencas;
    
    // Atualiza cards de resumo
    document.getElementById('relatorio-total-presencas').textContent = totalPresencas;
    document.getElementById('relatorio-media-horas').textContent = mediaHoras.toFixed(2) + 'h';
    document.getElementById('relatorio-total-horas').textContent = totalHoras.toFixed(2) + 'h';
    
    // Gera relatório por estagiário
    const relatorioEstagiarios = [];
    
    estagiarios.forEach(estagiario => {
        const presencasEstagiario = presencasFiltradas.filter(p => p.estagiarioId === estagiario.id);
        
        if (presencasEstagiario.length > 0) {
            let horasEstagiario = 0;
            presencasEstagiario.forEach(p => {
                if (p.horas) {
                    const [horas, minutos] = p.horas.split(':').map(Number);
                    horasEstagiario += horas + (minutos / 60);
                }
            });
            
            relatorioEstagiarios.push({
                nome: estagiario.nome,
                totalPresencas: presencasEstagiario.length,
                totalHoras: horasEstagiario.toFixed(2),
                mediaDiaria: (horasEstagiario / presencasEstagiario.length).toFixed(2)
            });
        }
    });
    
    // Preenche tabela do relatório
    const tableBody = document.querySelector('#relatorio-tabela tbody');
    tableBody.innerHTML = '';
    
    relatorioEstagiarios.forEach(rel => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${rel.nome}</td>
            <td>${rel.totalPresencas}</td>
            <td>${rel.totalHoras}h</td>
            <td>${rel.mediaDiaria}h</td>
        `;
        tableBody.appendChild(row);
    });
    
    showToast('Relatório gerado com sucesso!', 'success');
}

// Exportar relatório
function exportarRelatorio() {
    const tableData = document.querySelector('#relatorio-tabela').outerHTML;
    const mesNome = document.querySelector('#relatorio-mes option:checked').textContent;
    const ano = document.getElementById('relatorio-ano').value;
    
    if (!tableData.includes('<tr>')) {
        showToast('Gere um relatório antes de exportar', 'error');
        return;
    }
    
    const blob = new Blob([`
        <html>
            <head>
                <title>Relatório de Estagiários - ${mesNome}/${ano}</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    h1 { color: #333; }
                    table { border-collapse: collapse; width: 100%; margin-top: 20px; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                </style>
            </head>
            <body>
                <h1>Relatório de Estagiários - ${mesNome}/${ano}</h1>
                <p>Data de geração: ${new Date().toLocaleDateString()}</p>
                <div>
                    <p><strong>Total de Presenças:</strong> ${document.getElementById('relatorio-total-presencas').textContent}</p>
                    <p><strong>Média de Horas por Dia:</strong> ${document.getElementById('relatorio-media-horas').textContent}</p>
                    <p><strong>Total de Horas:</strong> ${document.getElementById('relatorio-total-horas').textContent}</p>
                </div>
                ${tableData}
            </body>
        </html>
    `], { type: 'text/html' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `relatorio-estagiarios-${mesNome}-${ano}.html`;
    link.click();
    
    showToast('Relatório exportado com sucesso!', 'success');
}

// Define a data padrão para o relatório (mês atual)
function setReportDefaultDate() {
    const mesAtual = hoje.getMonth() + 1;
    const anoAtual = hoje.getFullYear();
    
    document.getElementById('relatorio-mes').value = mesAtual;
    document.getElementById('relatorio-ano').value = anoAtual;
}

// Função utilitária para mostrar toasts de notificação
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.classList.add('toast', type);
    
    let icon;
    switch (type) {
        case 'success':
            icon = '<i class="fas fa-check-circle"></i>';
            break;
        case 'error':
            icon = '<i class="fas fa-exclamation-circle"></i>';
            break;
        case 'warning':
            icon = '<i class="fas fa-exclamation-triangle"></i>';
            break;
        default:
            icon = '<i class="fas fa-info-circle"></i>';
    }
    
    toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-message">${message}</div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Exibe a notificação
    setTimeout(() => {
        toast.classList.add('active');
    }, 100);
    
    // Remove a notificação após 3 segundos
    setTimeout(() => {
        toast.classList.remove('active');
        setTimeout(() => {
            toastContainer.removeChild(toast);
        }, 300);
    }, 3000);
}

// Calcular horas entre entrada e saída
function calcularHoras(entrada, saida) {
    const [horaEntrada, minutoEntrada] = entrada.split(':').map(Number);
    const [horaSaida, minutoSaida] = saida.split(':').map(Number);
    
    let totalMinutos = (horaSaida * 60 + minutoSaida) - (horaEntrada * 60 + minutoEntrada);
    
    if (totalMinutos < 0) {
        // Caso a saída seja no dia seguinte (exemplo: entrou às 22:00 e saiu às 06:00)
        totalMinutos += 24 * 60;
    }
    
    const horas = Math.floor(totalMinutos / 60);
    const minutos = totalMinutos % 60;
    
    return `${horas}:${minutos.toString().padStart(2, '0')}`;
}

// Função para formatar data
function formatarData(dataString) {
    const data = new Date(dataString);
    const dia = data.getDate().toString().padStart(2, '0');
    const mes = (data.getMonth() + 1).toString().padStart(2, '0');
    const ano = data.getFullYear();
    return `${dia}/${mes}/${ano}`;
}
