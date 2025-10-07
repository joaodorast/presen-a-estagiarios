// Sistema de Controle de Estagiários (SEICE)
// Versão 1.0.0

// Mock data para simulação do sistema
let estagiarios = []

async function fetchEstagiarios() {
    try {
        const response = await fetch('/api/estagiarios/');
        if (!response.ok) {
            throw new Error('Erro ao carregar os estagiários');
        }
        const data = await response.json();
        estagiarios = data.estagiarios; // Atualiza a lista global de estagiários
        return estagiarios;
    } catch (error) {
        console.error(error);
        showToast('Erro ao carregar os estagiários', 'error');
    }
}

let presencas = []
async function fetchPresencas() {
    try {
        const response = await fetch('/api/presencas/');
        if (!response.ok) {
            throw new Error('Erro ao carregar as presenças');
        }
        const data = await response.json();
        presencas = data.presencas; // Atualiza a lista global de presenças
        console.log('Presenças carregadas:', presencas); // Depuração
        return presencas;
    } catch (error) {
        console.error(error);
        showToast('Erro ao carregar as presenças', 'error');
    }
}

let areas = [];
async function fetchAreas() {
    try {
        const response = await fetch('/api/areas/');
        if (!response.ok) throw new Error('Erro ao carregar as áreas');
        const data = await response.json();
        areas = data.areas || data; // Ajuste conforme resposta da API
        return areas;
    } catch (error) {
        console.error(error);
        showToast('Erro ao carregar as áreas', 'error');
    }
}

let presencasHoje = [];

const hoje = new Date();
const dataAtual = hoje.getFullYear() + '-' + String(hoje.getMonth() + 1).padStart(2, '0') + '-' + String(hoje.getDate()).padStart(2, '0');
const dataHojeFormatada = formatarData(dataAtual);

const dataHojeEl = document.getElementById('today-date');
if (dataHojeEl) {
    dataHojeEl.textContent = dataHojeFormatada;
}

const navItems = document.querySelectorAll('.sidebar nav ul li');
const pages = document.querySelectorAll('.page');

document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    initMenuToggle();
    initModals();
    
    // Primeiro carrega estagiários, depois presenças
    Promise.all([fetchEstagiarios(), fetchPresencas()])
        .then(() => {
            initTodayPresences();
            loadDashboardStats();
            loadPresencasTable();
        })
        .catch(error => {
            console.error('Erro ao carregar dados iniciais:', error);
            showToast('Erro ao carregar dados do sistema', 'error');
        });
        
    loadEstagiarios();
    initEventListeners();
    setReportDefaultDate();
});

function initNavigation() {
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            navItems.forEach(navItem => navItem.classList.remove('active'));
            this.classList.add('active');
            const pageId = this.getAttribute('data-page');
            pages.forEach(page => page.classList.remove('active'));
            document.getElementById(pageId).classList.add('active');

             if (pageId === 'areas') {
                loadAreas();
                initAreaSearch();
            } else if (pageId === 'estagiarios') {
                loadEstagiarios();
            }
        });
    });
}

document.getElementById('btn-calculadora-horas').addEventListener('click', function() {
    window.location.href = '/home/calculadora-horas/';
});

document.getElementById('btn-voltar-unidades').addEventListener('click', function() {
    window.location.href = '/home/'; // ajuste para a rota da seleção de unidades
});

function formatarHorasMinutos(valor) {
    const horas = Math.floor(valor);
    const minutos = Math.round((valor - horas) * 60);
    return `${horas}h ${minutos}m`;
}

function initMenuToggle() {
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    menuToggle.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
        mainContent.classList.toggle('expanded');
    });
}

function initModals() {
    const modals = document.querySelectorAll('.modal');
    const closeBtns = document.querySelectorAll('.close, .modal-cancel');
    
    // document.getElementById('btn-registrar-entrada').addEventListener('click', function() {
    //     openModal('modal-registrar-entrada');
    //     loadEstagiarioSelect('entrada-estagiario', true);
    // });
    
    // document.getElementById('btn-registrar-saida').addEventListener('click', function() {
    //     openModal('modal-registrar-saida');
    //     loadEstagiarioSelectWithPresence('saida-estagiario');
    // });
    
    document.getElementById('btn-novo-estagiario').addEventListener('click', function() {
        document.getElementById('modal-estagiario-titulo').textContent = 'Novo Estagiário';
        document.getElementById('estagiario-id').value = '';
        document.getElementById('estagiario-nome').value = '';
        document.getElementById('estagiario-area').value = '';
        document.getElementById('estagiario-email').value = '';
        document.getElementById('estagiario-data-inicio').value = dataAtual;
        document.getElementById('estagiario-ativo').value = 'true';
        document.getElementById('estagiario-control-id').value = '';
        loadAreaSelect('estagiario-area');
        openModal('modal-estagiario');
    });

    document.getElementById('btn-nova-area').addEventListener('click', function() {
        openAreaModal();
    });
    
    closeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            modals.forEach(modal => {
                modal.classList.remove('active');
            });
        });
    });
    
    window.addEventListener('click', function(event) {
        modals.forEach(modal => {
            if (event.target == modal) {
                modal.classList.remove('active');
            }
        });
    });
}

function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function loadAreas() {
    fetchAreas().then(() => {
        const tableBody = document.querySelector('#areas-tabela tbody');
        tableBody.innerHTML = '';

        if (!areas.length) {
            const row = document.createElement('tr');
            row.innerHTML = `<td colspan="5" class="text-center">Nenhuma área cadastrada.</td>`;
            tableBody.appendChild(row);
            return;
        }
        console.log('Áreas carregadas:', areas); // Depuração

        areas.forEach(area => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${area.nome}</td>
                <td>${area.total_estagiarios || 0}</td>
                <td>
                    <div class="actions-column">
                        <button class="btn-icon edit" data-id="${area.id}"><i class="fas fa-edit"></i></button>
                        <button class="btn-icon delete" data-id="${area.id}"><i class="fas fa-trash-alt"></i></button>
                    </div>
                </td>
            `;
            tableBody.appendChild(row);
        });

        document.querySelectorAll('#areas-tabela .btn-icon.edit').forEach(btn => {
            btn.addEventListener('click', function () {
                const id = parseInt(this.getAttribute('data-id'));
                editArea(id);
            });
        });
        document.querySelectorAll('#areas-tabela .btn-icon.delete').forEach(btn => {
            btn.addEventListener('click', function () {
                const id = parseInt(this.getAttribute('data-id'));
                if (confirm('Tem certeza que deseja excluir esta área?')) {
                    deleteArea(id);
                }
            });
        });
    });
}

function openAreaModal(area = null) {
    let modal = document.getElementById('modal-area');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'modal-area';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3 id="modal-area-titulo">Nova Área</h3>
                    <span class="close">&times;</span>
                </div>
                <div class="modal-body">
                    <input type="hidden" id="area-id">
                    <div class="form-group">
                        <label for="area-nome">Nome:</label>
                        <input type="text" id="area-nome" required>
                    </div>
                </div>
                <div class="modal-footer">
                    <button id="btn-salvar-area" class="btn primary">Salvar</button>
                    <button class="btn secondary modal-cancel">Cancelar</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        modal.querySelector('.close').onclick = () => modal.classList.remove('active');
        modal.querySelector('.modal-cancel').onclick = () => modal.classList.remove('active');
    }

    document.getElementById('modal-area-titulo').textContent = area ? 'Editar Área' : 'Nova Área';
    document.getElementById('area-id').value = area ? area.id : '';
    document.getElementById('area-nome').value = area ? area.nome : '';

    document.getElementById('btn-salvar-area').onclick = salvarArea;

    modal.classList.add('active');
}

function salvarArea() {
    const id = document.getElementById('area-id').value;
    const nome = document.getElementById('area-nome').value.trim();

    if (!nome) {
        showToast('O nome da área é obrigatório', 'error');
        return;
    }

    const area = { nome };

    let url = '/api/areas/create/';
    let method = 'POST';
    if (id) {
        method = 'PUT';
        area.id = parseInt(id);
    }

    fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(area)
    })
        .then(response => {
            if (!response.ok) throw new Error('Erro ao salvar a área');
            return response.json();
        })
        .then(() => {
            showToast(id ? 'Área atualizada com sucesso!' : 'Área cadastrada com sucesso!', 'success');
            document.getElementById('modal-area').classList.remove('active');
            loadAreas();
        })
        .catch(error => {
            console.error(error);
            showToast('Erro ao salvar a área', 'error');
        });
}

function editArea(id) {
    const area = areas.find(a => a.id === id);
    if (area) openAreaModal(area);
}

function deleteArea(id) {
    fetch(`/api/areas/${id}/delete/`, { method: 'DELETE' })
        .then(response => {
            if (!response.ok) throw new Error('Erro ao excluir a área');
            showToast('Área excluída com sucesso!', 'success');
            loadAreas();
        })
        .catch(error => {
            console.error(error);
            showToast('Erro ao excluir a área', 'error');
        });
}

function initAreaSearch() {
    const searchInput = document.getElementById('search-area');
    if (!searchInput) return;
    searchInput.addEventListener('input', function () {
        const searchTerm = this.value.toLowerCase();
        const filtered = areas.filter(area =>
            area.nome.toLowerCase().includes(searchTerm) 
        );
        renderAreasTable(filtered);
    });
}

function renderAreasTable(areasToShow) {
    const tableBody = document.querySelector('#areas-tabela tbody');
    tableBody.innerHTML = '';
    if (!areasToShow.length) {
        const row = document.createElement('tr');
        row.innerHTML = `<td colspan="5" class="text-center">Nenhuma área encontrada.</td>`;
        tableBody.appendChild(row);
        return;
    }
    console.log('Áreas a serem exibidas:', areasToShow); // Depuração
    areasToShow.forEach(area => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${area.nome}</td>
            <td>${area.total_estagiarios || 0}</td>
            <td>
                <div class="actions-column">
                    <button class="btn-icon edit" data-id="${area.id}"><i class="fas fa-edit"></i></button>
                    <button class="btn-icon delete" data-id="${area.id}"><i class="fas fa-trash-alt"></i></button>
                </div>
            </td>
        `;
        tableBody.appendChild(row);
    });

    document.querySelectorAll('#areas-tabela .btn-icon.edit').forEach(btn => {
        btn.addEventListener('click', function () {
            const id = parseInt(this.getAttribute('data-id'));
            editArea(id);
        });
    });
    document.querySelectorAll('#areas-tabela .btn-icon.delete').forEach(btn => {
        btn.addEventListener('click', function () {
            const id = parseInt(this.getAttribute('data-id'));
            if (confirm('Tem certeza que deseja excluir esta área?')) {
                deleteArea(id);
            }
        });
    });
}

// CORREÇÃO PRINCIPAL - Função que sempre mostra todos os estagiários ativos
function initTodayPresences() {
    presencasHoje = presencas.filter(p => {
        return p.data === dataAtual;
    });

    console.log('Presenças de hoje:', presencasHoje);
    // Sempre carrega a tabela, mesmo se não houver presenças
    loadTodayPresencesTable();
}

function loadDashboardStats() {
    document.getElementById('total-estagiarios').textContent = estagiarios.filter(e => e.ativo).length;

    document.getElementById('presentes-hoje').textContent = presencasHoje.length;

    const mesAtual = hoje.getMonth() + 1;
    const anoAtual = hoje.getFullYear();
    const presencasMes = presencas.filter(p => {
        const [year, month, day] = p.data.split('-').map(Number);
        return month === mesAtual && year === anoAtual;
    });
    document.getElementById('presencas-mes').textContent = presencasMes.length;

    let horasTotais = 0;
    presencasMes.forEach(p => {
        if (p.horas) { // Verifica se o campo 'horas' não é null ou undefined
            const [horas, minutos] = p.horas.split(':').map(Number);
            horasTotais += horas + (minutos / 60);
        }
    });
    document.getElementById('horas-mes').textContent = formatarHorasMinutos(horasTotais);
}

// CORREÇÃO PRINCIPAL - Mostra todos os estagiários ativos
function loadTodayPresencesTable() {
    const tableBody = document.querySelector('#presencas-hoje-tabela tbody');
    tableBody.innerHTML = '';
    
    // Buscar todos os estagiários ativos
    const estagiarios_ativos = estagiarios.filter(e => e.ativo);
    
    if (estagiarios_ativos.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `<td colspan="4" class="text-center">Nenhum estagiário ativo encontrado.</td>`;
        tableBody.appendChild(row);
        return;
    }
    
    // Para cada estagiário ativo, verificar se tem presença hoje
    estagiarios_ativos.forEach(estagiario => {
        const presencaHoje = presencasHoje.find(p => p.estagiario_id === estagiario.id);
        
        const row = document.createElement('tr');
        
        if (presencaHoje) {
            // Estagiário tem presença registrada hoje
            row.innerHTML = `
                <td>${estagiario.nome}</td>
                <td>${presencaHoje.entrada}</td>
                <td>${presencaHoje.saida || '---'}</td>
                <td>
                    <span class="badge ${presencaHoje.saida ? 'inactive' : 'active'}">
                        ${presencaHoje.saida ? 'Finalizado' : 'Em andamento'}
                    </span>
                </td>
            `;
        } else {
            // Estagiário não tem presença registrada hoje
            row.innerHTML = `
                <td>${estagiario.nome}</td>
                <td>---</td>
                <td>---</td>
                <td>
                    <span class="badge" style="background-color: #6c757d; color: white;">
                        Não registrado
                    </span>
                </td>
            `;
        }
        
        tableBody.appendChild(row);
    });
}

function loadEstagiarios() {
    fetchEstagiarios().then(() => {
        const tableBody = document.querySelector('#estagiarios-tabela tbody');
        tableBody.innerHTML = '';

        if (estagiarios.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = `<td colspan="8" class="text-center">Nenhum estagiário encontrado.</td>`;
            tableBody.appendChild(row);
            return;
        }

        estagiarios.forEach(estagiario => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${estagiario.nome}</td>
                <td>${estagiario.area_nome || estagiario.area || 'N/A'}</td>
                <td>${estagiario.email}</td>
                <td>${formatarData(estagiario.data_inicio)}</td>
                <td>
                    <span class="badge ${estagiario.ativo ? 'active' : 'inactive'}">
                        ${estagiario.ativo ? 'Ativo' : 'Inativo'}
                    </span>
                </td>
                <td>
                    <div class="actions-column">
                        <button class="btn-icon edit" data-id="${estagiario.id}" title="Editar">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn-icon delete" data-id="${estagiario.id}" title="Excluir">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                </td>
            `;
            tableBody.appendChild(row);
        });

        // Adicionar eventos para edição e exclusão
        tableBody.querySelectorAll('.btn-icon.edit').forEach(btn => {
            btn.addEventListener('click', function () {
                const id = parseInt(this.getAttribute('data-id'));
                editEstagiario(id);
            });
        });

        tableBody.querySelectorAll('.btn-icon.delete').forEach(btn => {
            btn.addEventListener('click', function () {
                const id = parseInt(this.getAttribute('data-id'));
                if (confirm('Tem certeza que deseja excluir este estagiário?')) {
                    deleteEstagiario(id);
                }
            });
        });
    });
}

function loadAreaSelect(selectId) {
    return fetchAreas().then(() => {
        const select = document.getElementById(selectId);
        select.innerHTML = '<option value="">Selecione a área</option>';
        areas.forEach(area => {
            const option = document.createElement('option');
            option.value = area.id;
            option.textContent = area.nome;
            select.appendChild(option);
            console.log(`Adicionando área ao select: ${area.nome}`); // Depuração
        });
    });
}

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
        let horasFormatadas = '---';
        if (presenca.horas) {
            if (presenca.horas.includes(':')) {
                const [h, m] = presenca.horas.split(':').map(Number);
                horasFormatadas = formatarHorasMinutos(h + m / 60);
            } else {
                horasFormatadas = formatarHorasMinutos(parseFloat(presenca.horas));
            }
        }
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${presenca.estagiario__nome}</td>
            <td>${formatarData(presenca.data)}</td>
            <td>${presenca.entrada}</td>
            <td>${presenca.saida || '---'}</td>
            <td>${horasFormatadas}</td>
            <td>${presenca.observacao || '---'}</td>
            <td>
                <button class="btn-icon edit-presenca" data-id="${presenca.id}" title="Editar">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn-icon delete-presenca" data-id="${presenca.id}" title="Excluir">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </td>
        `;
        tableBody.appendChild(row);
    });

    // Adicionar eventos
    tableBody.querySelectorAll('.edit-presenca').forEach(btn => {
        btn.addEventListener('click', function () {
            const id = parseInt(this.getAttribute('data-id'));
            abrirModalEditarPresenca(id);
        });
    });
    tableBody.querySelectorAll('.delete-presenca').forEach(btn => {
        btn.addEventListener('click', function () {
            const id = parseInt(this.getAttribute('data-id'));
            deletarPresenca(id);
        });
    });
}

function loadEstagiarioSelect(selectId, onlyActive = false) {
    fetchEstagiarios().then(() => {
        const select = document.getElementById(selectId);
        select.innerHTML = '<option value="">Selecione o estagiário</option>';

        const filteredEstagiarios = onlyActive ? estagiarios.filter(e => e.ativo) : estagiarios;

        filteredEstagiarios.forEach(estagiario => {
            const option = document.createElement('option');
            option.value = estagiario.id;
            option.textContent = estagiario.nome;
            select.appendChild(option);
        });
    });
}

function loadEstagiarioSelectWithPresence(selectId) {
    const select = document.getElementById(selectId);
    select.innerHTML = '<option value="">Selecione o estagiário</option>';
    
    const estagiariosPresentesHoje = presencasHoje
        .filter(p => !p.saida)
        .map(p => p.estagiario_id);
    
    estagiarios
        .filter(e => e.ativo && estagiariosPresentesHoje.includes(e.id))
        .forEach(estagiario => {
            const option = document.createElement('option');
            option.value = estagiario.id;
            option.textContent = estagiario.nome;
            select.appendChild(option);
        });
}

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

function initEventListeners() {
    document.getElementById('btn-confirmar-entrada').addEventListener('click', registrarEntrada);
    document.getElementById('btn-confirmar-saida').addEventListener('click', registrarSaida);
    document.getElementById('btn-salvar-estagiario').addEventListener('click', salvarEstagiario);
    document.getElementById('btn-filtrar-presencas').addEventListener('click', filtrarPresencas);
    document.getElementById('btn-gerar-relatorio').addEventListener('click', gerarRelatorio);
    document.getElementById('btn-exportar-relatorio').addEventListener('click', exportarRelatorio);
    
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
    });
    
    document.querySelector('[data-page="presencas"]').addEventListener('click', function() {
        loadEstagiarioFilter();
        const today = new Date();
        const lastMonth = new Date();
        lastMonth.setMonth(today.getMonth() - 1);
        
        document.getElementById('filtro-data-fim').value = today.toISOString().split('T')[0];
        document.getElementById('filtro-data-inicio').value = lastMonth.toISOString().split('T')[0];
    });
}

function registrarEntrada() {
    const estagiarioId = parseInt(document.getElementById('entrada-estagiario').value);
    const observacao = document.getElementById('entrada-observacao').value;

    if (!estagiarioId) {
        showToast('Por favor, selecione um estagiário', 'error');
        return;
    }

    const jaPresente = presencasHoje.some(p => p.estagiario_id === estagiarioId && !p.saida);
    console.log('Verificando presença:', jaPresente); // Depuração
    if (jaPresente) {
        console.log('Estagiário ja presente hoje!');
        showToast('Este estagiário já está presente hoje!', 'warning');
        return;
    }

    const horaAtual = new Date().toTimeString().split(' ')[0];
    const novaPresenca = {
        estagiarioId: estagiarioId,
        data: dataAtual,
        entrada: horaAtual,
        observacao: observacao
    };

    fetch('/api/presencas/entrada/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(novaPresenca),
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao registrar entrada');
            }
            return response.json();
        })
        .then(data => {
            showToast('Entrada registrada com sucesso!', 'success');
            fetchPresencas().then(() => {
                    initTodayPresences();
                    loadDashboardStats();
                    loadPresencasTable();
                }); // Atualiza a tabela
        })
        .catch(error => {
            console.error(error);
            showToast('Erro ao registrar entrada', 'error');
        });

    document.getElementById('modal-registrar-entrada').classList.remove('active');
    document.getElementById('entrada-estagiario').value = '';
    document.getElementById('entrada-observacao').value = '';
}

function registrarSaida() {
    const estagiarioId = parseInt(document.getElementById('saida-estagiario').value);
    const observacao = document.getElementById('saida-observacao').value;

    if (!estagiarioId) {
        showToast('Por favor, selecione um estagiário', 'error');
        return;
    }

    const presenca = presencas.find(p => p.estagiario_id === estagiarioId && !p.saida);
    if (!presenca) {
        showToast('Não foi encontrada entrada aberta para este estagiário', 'error');
        return;
    }

    const horaAtual = new Date().toTimeString().split(' ')[0];
    const horas = calcularHoras(presenca.entrada, horaAtual);

    const dadosSaida = {
        presencaId: presenca.id,
        saida: horaAtual,
        horas: horas,
        observacao: observacao
    };
    fetch('/api/presencas/saida/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(dadosSaida),
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao registrar saída');
            }
            return response.json();
        })
        .then(data => {
            showToast('Saída registrada com sucesso!', 'success');
           fetchPresencas().then(() => {
                    initTodayPresences();
                    loadDashboardStats();
                    loadPresencasTable();
                }); // Atualiza a tabela
        })
        .catch(error => {
            console.error(error);
            showToast('Erro ao registrar saída', 'error');
        });

    document.getElementById('modal-registrar-saida').classList.remove('active');
    document.getElementById('saida-estagiario').value = '';
    document.getElementById('saida-observacao').value = '';
}

function editEstagiario(id) {
    const estagiario = estagiarios.find(e => e.id === id);
    if (!estagiario) return;
    
    document.getElementById('modal-estagiario-titulo').textContent = 'Editar Estagiário';
    document.getElementById('estagiario-id').value = estagiario.id;
    document.getElementById('estagiario-nome').value = estagiario.nome;
    document.getElementById('estagiario-email').value = estagiario.email;
    document.getElementById('estagiario-data-inicio').value = estagiario.data_inicio;
    document.getElementById('estagiario-ativo').value = estagiario.ativo.toString();
    document.getElementById('estagiario-control-id').value = estagiario.control_id_user_id || '';

    // Carrega as áreas e só depois seleciona a área do estagiário
   loadAreaSelect('estagiario-area').then(() => {
    console.log('Valor de area_id:', estagiario.area_id); // Depuração
    document.getElementById('estagiario-area').value = estagiario.area_id || '';
});

    openModal('modal-estagiario');
}
// Salvar estagiário (novo ou editado)
function salvarEstagiario() {
    const id = document.getElementById('estagiario-id').value;
    const nome = document.getElementById('estagiario-nome').value;
    const area = document.getElementById('estagiario-area').value;
    const email = document.getElementById('estagiario-email').value;
    const dataInicio = document.getElementById('estagiario-data-inicio').value;
    const ativo = document.getElementById('estagiario-ativo').value === 'true';
    const controlIdUserId = document.getElementById('estagiario-control-id').value;

    const estagiario = {
        id: id ? parseInt(id) : null,
        nome,
        area: area ? parseInt(area) : null, // <-- sempre número!
        email,
        dataInicio,
        ativo,
        control_id_user_id: controlIdUserId,
        
    };
    
    if (!nome || !email || !dataInicio) {
        showToast('Por favor, preencha todos os campos obrigatórios', 'error');
        return;
    }
    
    if (id) {
        const index = estagiarios.findIndex(e => e.id === parseInt(id));
        if (index !== -1) {
            estagiarios[index] = {
                id: parseInt(id),
                nome,
                area,
                email,
                dataInicio,
                ativo,
                control_id_user_id: controlIdUserId
            };
        }
    } else {
        // Novo estagiário
        const novoId = estagiarios.length > 0 ? Math.max(...estagiarios.map(e => e.id)) + 1 : 1;
        estagiarios.push({
            id: novoId,
            nome,
            area,
            email,
            dataInicio,
            ativo,
            control_id_user_id: controlIdUserId
        });
    }

   
    
    fetch('/api/estagiarios/create/', {
        method: id ? 'PUT' : 'POST', // PUT para edição, POST para criação
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(estagiario),
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao salvar o estagiário');
            }
            return response.json();
        })
        .then(data => {
            showToast(id ? 'Estagiário atualizado com sucesso!' : 'Estagiário cadastrado com sucesso!', 'success');
            document.getElementById('modal-estagiario').classList.remove('active');
            loadEstagiarios(); // Atualizar a lista de estagiários
        })
        .catch(error => {
            console.error(error);
            showToast('Erro ao salvar o estagiário', 'error');
        });
}

function deleteEstagiario(id) {
    const temPresencas = presencas.some(p => p.estagiarioId === id);
    
    if (temPresencas) {
        showToast('Não é possível excluir este estagiário pois há presenças registradas', 'error');
        return;
    }
    
    const index = estagiarios.findIndex(e => e.id === id);

    if (index !== -1) {
        estagiarios.splice(index, 1);
        fetchEstagiarios();
        fetch(`/api/estagiarios/${id}/delete/`, {
            method: 'DELETE',
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro ao excluir o estagiário');
                }
                return response.json();
            })
            .then(data => {
                showToast('Estagiário excluído com sucesso!', 'success');
            })
            .catch(error => {
                console.error(error);
                showToast('Erro ao excluir o estagiário', 'error');
            });
            
        loadEstagiarios();
        loadDashboardJs();
    }
}

function filtrarPresencas() {
    const estagiarioId = document.getElementById('filtro-estagiario').value;
    const dataInicio = document.getElementById('filtro-data-inicio').value;
    const dataFim = document.getElementById('filtro-data-fim').value;
    
    let filtered = [...presencas];
    
    if (estagiarioId) {
        filtered = filtered.filter(p => p.estagiario_id === parseInt(estagiarioId));
    }
    
    if (dataInicio) {
        filtered = filtered.filter(p => p.data >= dataInicio);
    }
    
    if (dataFim) {
        filtered = filtered.filter(p => p.data <= dataFim);
    }
    
    loadPresencasTable(filtered);
}

function gerarRelatorio() {
    const mes = parseInt(document.getElementById('relatorio-mes').value);
    const ano = parseInt(document.getElementById('relatorio-ano').value);
    
    if (!mes || !ano) {
        showToast('Por favor, selecione o mês e o ano', 'error');
        return;
    }

    const presencasFiltradas = presencas.filter(p => {
        const [year, month, day] = p.data.split('-').map(Number);
        return month === mes && year === ano;
    });
    
    if (presencasFiltradas.length === 0) {
        showToast('Não há dados para o período selecionado', 'warning');
        return;
    }
    
    const totalPresencas = presencasFiltradas.length;
    
    let totalHoras = 0;
    presencasFiltradas.forEach(p => {
        if (p.horas) {
            const [horas, minutos] = p.horas.split(':').map(Number);
            totalHoras += horas + (minutos / 60);
        }
    });
    
    const mediaHoras = totalHoras / totalPresencas;
    
    document.getElementById('relatorio-total-presencas').textContent = totalPresencas;
    document.getElementById('relatorio-media-horas').textContent = formatarHorasMinutos(mediaHoras);
    document.getElementById('relatorio-total-horas').textContent = formatarHorasMinutos(totalHoras);

    
    const relatorioEstagiarios = [];
    
    estagiarios.forEach(estagiario => {
        const presencasEstagiario = presencasFiltradas.filter(p => p.estagiario_id === estagiario.id);
        
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
                totalHoras: formatarHorasMinutos(horasEstagiario),
                mediaDiaria: formatarHorasMinutos(horasEstagiario / presencasEstagiario.length)
            });
        }
    });
    
    const tableBody = document.querySelector('#relatorio-tabela tbody');
    tableBody.innerHTML = '';
    
    relatorioEstagiarios.forEach(rel => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${rel.nome}</td>
            <td>${rel.totalPresencas}</td>
            <td>${rel.totalHoras}</td>
            <td>${rel.mediaDiaria}</td>
        `;
        tableBody.appendChild(row);
    });
    
    showToast('Relatório gerado com sucesso!', 'success');
}

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

function setReportDefaultDate() {
    const mesAtual = hoje.getMonth() + 1;
    const anoAtual = hoje.getFullYear();
    
    document.getElementById('relatorio-mes').value = mesAtual;
    document.getElementById('relatorio-ano').value = anoAtual;
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    console.log('Exibindo toast:', message, type, toastContainer); // Depuração
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
    
    setTimeout(() => {
        toast.classList.add('active');
    }, 100);
    
    setTimeout(() => {
        toast.classList.remove('active');
        setTimeout(() => {
            toastContainer.removeChild(toast);
        }, 300);
    }, 3000);
}

function calcularHoras(entrada, saida) {
    const [horaEntrada, minutoEntrada] = entrada.split(':').map(Number);
    const [horaSaida, minutoSaida] = saida.split(':').map(Number);
    
    let totalMinutos = (horaSaida * 60 + minutoSaida) - (horaEntrada * 60 + minutoEntrada);
    
    if (totalMinutos < 0) {
        totalMinutos += 24 * 60;
    }
    
    const horas = Math.floor(totalMinutos / 60);
    const minutos = totalMinutos % 60;
    
    return `${horas}:${minutos.toString().padStart(2, '0')}`;
}

function formatarData(dataString) {
    const data = new Date(dataString);
    const dia = data.getDate().toString().padStart(2, '0');
    const mes = (data.getMonth() + 1).toString().padStart(2, '0');
    const ano = data.getFullYear();
    return `${dia}/${mes}/${ano}`;
}

// MODAL DE CONFIRMAÇÃO DE EXCLUSÃO
let areaIdParaExcluir = null;
let areaNomeParaExcluir = null;

function confirmarExclusaoArea(id, nome) {
    areaIdParaExcluir = id;
    areaNomeParaExcluir = nome;
    
    document.getElementById('area-nome-exclusao').textContent = nome;
    document.getElementById('modal-confirmar-exclusao').classList.add('active');
}

function fecharModalConfirmacao() {
    document.getElementById('modal-confirmar-exclusao').classList.remove('active');
    areaIdParaExcluir = null;
    areaNomeParaExcluir = null;
}

function executarExclusao() {
    if (areaIdParaExcluir) {
        console.log(`Excluindo área ID: ${areaIdParaExcluir}, Nome: ${areaNomeParaExcluir}`);
        
        const linha = document.querySelector(`tr:has(td:first-child:contains('${areaIdParaExcluir}'))`);
        if (linha) {
            linha.remove();
        }
        
        showToast('Área excluída com sucesso!', 'success');
        fecharModalConfirmacao();
    }
}

function abrirModalEditarPresenca(id) {
    const presenca = presencas.find(p => p.id === id);
    if (!presenca) return;
    document.getElementById('presenca-edit-id').value = presenca.id;
    document.getElementById('presenca-edit-entrada').value = presenca.entrada ? presenca.entrada.slice(0,5) : '';
    document.getElementById('presenca-edit-saida').value = presenca.saida ? presenca.saida.slice(0,5) : '';
    document.getElementById('presenca-edit-observacao').value = presenca.observacao || '';
    document.getElementById('modal-editar-presenca').classList.add('active');
}

function salvarEdicaoPresenca() {
    const id = document.getElementById('presenca-edit-id').value;
    const entrada = document.getElementById('presenca-edit-entrada').value;
    const saida = document.getElementById('presenca-edit-saida').value;
    const observacao = document.getElementById('presenca-edit-observacao').value;

    if (!entrada) {
        showToast('Preencha o horário de entrada', 'error');
        return;
    }

    // Calcula horas se saída preenchida
    let horas = '';
    if (entrada && saida) {
        horas = calcularHoras(entrada, saida);
    }

    fetch(`/api/presencas/${id}/edit/`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            entrada,
            saida,
            horas,
            observacao
        })
    })
    .then(response => {
        if (!response.ok) throw new Error('Erro ao editar presença');
        return response.json();
    })
    .then(() => {
        showToast('Presença editada com sucesso!', 'success');
        document.getElementById('modal-editar-presenca').classList.remove('active');
        fetchPresencas().then(loadPresencasTable);
    })
    .catch(error => {
        console.error(error);
        showToast('Erro ao editar presença', 'error');
    });
}

function deletarPresenca(id) {
    if (!confirm('Tem certeza que deseja excluir esta presença?')) return;
    fetch(`/api/presencas/${id}/delete/`, {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) throw new Error('Erro ao excluir presença');
        return response.json();
    })
    .then(() => {
        showToast('Presença excluída com sucesso!', 'success');
        fetchPresencas().then(loadPresencasTable);
    })
    .catch(error => {
        console.error(error);
        showToast('Erro ao excluir presença', 'error');
    });
}