 document.addEventListener('DOMContentLoaded', () => {
            const hoje = new Date().toISOString().split('T')[0];
            document.getElementById('data').value = hoje;
            
            
            carregarDados();
            
            
            document.querySelectorAll('.tab-btn').forEach(button => {
                button.addEventListener('click', () => {
                    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
                    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                    
                    button.classList.add('active');
                    document.getElementById(button.dataset.tab).classList.add('active');
                });
            });
            
            
            document.getElementById('registrar-presenca').addEventListener('click', registrarPresenca);
            document.getElementById('cadastrar-estagiario').addEventListener('click', cadastrarEstagiario);
            document.getElementById('gerar-relatorio').addEventListener('click', gerarRelatorio);
            document.getElementById('busca-estagiario').addEventListener('input', filtrarEstagiarios);
        });
        
       
        function carregarDados() {
           
            const estagiarios = JSON.parse(localStorage.getItem('estagiarios')) || [];
            const selectEstagiario = document.getElementById('estagiario');
            const selectRelatorioEstagiario = document.getElementById('relatorio-estagiario');
            
            
            selectEstagiario.innerHTML = '<option value="">Selecione um estagiário</option>';
            selectRelatorioEstagiario.innerHTML = '<option value="">Todos os estagiários</option>';
            
            
            estagiarios.forEach(estagiario => {
                const option = document.createElement('option');
                option.value = estagiario.id;
                option.textContent = estagiario.nome;
                selectEstagiario.appendChild(option);
                
                const optionRelatorio = option.cloneNode(true);
                selectRelatorioEstagiario.appendChild(optionRelatorio);
            });
            
         
            atualizarListaEstagiarios(estagiarios);
            
            
            atualizarRegistrosHoje();
        }
        
        function atualizarListaEstagiarios(estagiarios) {
            const listaEstagiarios = document.getElementById('lista-estagiarios');
            listaEstagiarios.innerHTML = '';
            
            if (estagiarios.length === 0) {
                listaEstagiarios.innerHTML = '<p>Nenhum estagiário cadastrado.</p>';
                return;
            }
            
            estagiarios.forEach(estagiario => {
                const div = document.createElement('div');
                div.className = 'estagiario-item';
                div.innerHTML = `
                    <h3>${estagiario.nome}</h3>
                    <p><strong>Matrícula:</strong> ${estagiario.matricula}</p>
                    <p><strong>Departamento:</strong> ${estagiario.departamento}</p>
                    <p><strong>Supervisor:</strong> ${estagiario.supervisor}</p>
                    <button class="excluir-estagiario" data-id="${estagiario.id}">Excluir</button>
                `;
                listaEstagiarios.appendChild(div);
            });
            
           
            document.querySelectorAll('.excluir-estagiario').forEach(button => {
                button.addEventListener('click', function() {
                    excluirEstagiario(this.dataset.id);
                });
            });
        }
        
        function atualizarRegistrosHoje() {
            const hoje = new Date().toISOString().split('T')[0];
            const registros = JSON.parse(localStorage.getItem('registros')) || [];
            const registrosHoje = registros.filter(registro => registro.data === hoje);
            
            const tbody = document.querySelector('#registros-hoje tbody');
            tbody.innerHTML = '';
            
            if (registrosHoje.length === 0) {
                const tr = document.createElement('tr');
                tr.innerHTML = '<td colspan="4" style="text-align: center;">Nenhum registro para hoje.</td>';
                tbody.appendChild(tr);
                return;
            }
            
            const estagiarios = JSON.parse(localStorage.getItem('estagiarios')) || [];
            
            registrosHoje.forEach(registro => {
                const estagiario = estagiarios.find(e => e.id === registro.estagiarioId);
                const nomeEstagiario = estagiario ? estagiario.nome : 'Desconhecido';
                
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${nomeEstagiario}</td>
                    <td>${registro.horaEntrada || '-'}</td>
                    <td>${registro.horaSaida || '-'}</td>
                    <td>${registro.observacao || '-'}</td>
                `;
                tbody.appendChild(tr);
            });
        }
        
        function registrarPresenca() {
            const estagiarioId = document.getElementById('estagiario').value;
            const data = document.getElementById('data').value;
            const horaEntrada = document.getElementById('hora-entrada').value;
            const horaSaida = document.getElementById('hora-saida').value;
            const observacao = document.getElementById('observacao').value;
            
            if (!estagiarioId) {
                mostrarAlerta('Selecione um estagiário', 'error');
                return;
            }
            
            if (!data) {
                mostrarAlerta('Selecione uma data', 'error');
                return;
            }
            
            if (!horaEntrada && !horaSaida) {
                mostrarAlerta('Informe pelo menos uma hora (entrada ou saída)', 'error');
                return;
            }
            
           
            const registros = JSON.parse(localStorage.getItem('registros')) || [];
            const registroExistente = registros.findIndex(r => 
                r.estagiarioId === estagiarioId && r.data === data
            );
            
            if (registroExistente >= 0) {
               
                if (horaEntrada) registros[registroExistente].horaEntrada = horaEntrada;
                if (horaSaida) registros[registroExistente].horaSaida = horaSaida;
                if (observacao) registros[registroExistente].observacao = observacao;
            } else {
               
                const novoRegistro = {
                    id: Date.now().toString(),
                    estagiarioId,
                    data,
                    horaEntrada,
                    horaSaida,
                    observacao
                };
                registros.push(novoRegistro);
            }
            
            
            localStorage.setItem('registros', JSON.stringify(registros));
            
          
            atualizarRegistrosHoje();
            
           
            document.getElementById('hora-entrada').value = '';
            document.getElementById('hora-saida').value = '';
            document.getElementById('observacao').value = '';
            
            mostrarAlerta('Presença registrada com sucesso!', 'success');
        }
        
        function cadastrarEstagiario() {
            const nome = document.getElementById('nome').value;
            const matricula = document.getElementById('matricula').value;
            const departamento = document.getElementById('departamento').value;
            const supervisor = document.getElementById('supervisor').value;
            
            if (!nome || !matricula) {
                mostrarAlerta('Nome e matrícula são obrigatórios', 'error');
                return;
            }
            
           
            const estagiarios = JSON.parse(localStorage.getItem('estagiarios')) || [];
            if (estagiarios.some(e => e.matricula === matricula)) {
                mostrarAlerta('Já existe um estagiário com esta matrícula', 'error');
                return;
            }
            
            const novoEstagiario = {
                id: Date.now().toString(),
                nome,
                matricula,
                departamento,
                supervisor
            };
            
            estagiarios.push(novoEstagiario);
            localStorage.setItem('estagiarios', JSON.stringify(estagiarios));
            
            
            document.getElementById('nome').value = '';
            document.getElementById('matricula').value = '';
            document.getElementById('departamento').value = '';
            document.getElementById('supervisor').value = '';
            
            
            carregarDados();
            
            mostrarAlerta('Estagiário cadastrado com sucesso!', 'success');
        }
        
        function excluirEstagiario(id) {
            if (confirm('Tem certeza que deseja excluir este estagiário? Todos os seus registros de presença também serão excluídos.')) {
                let estagiarios = JSON.parse(localStorage.getItem('estagiarios')) || [];
                estagiarios = estagiarios.filter(e => e.id !== id);
                localStorage.setItem('estagiarios', JSON.stringify(estagiarios));
                
               
                let registros = JSON.parse(localStorage.getItem('registros')) || [];
                registros = registros.filter(r => r.estagiarioId !== id);
                localStorage.setItem('registros', JSON.stringify(registros));
                
               
                carregarDados();
                
                mostrarAlerta('Estagiário excluído com sucesso!', 'success');
            }
        }
        
        function filtrarEstagiarios() {
            const termo = document.getElementById('busca-estagiario').value.toLowerCase();
            const estagiarios = JSON.parse(localStorage.getItem('estagiarios')) || [];
            
            const estagiariosFiltrados = estagiarios.filter(e => 
                e.nome.toLowerCase().includes(termo) || 
                e.matricula.toLowerCase().includes(termo) ||
                e.departamento.toLowerCase().includes(termo) ||
                e.supervisor.toLowerCase().includes(termo)
            );
            
            atualizarListaEstagiarios(estagiariosFiltrados);
        }
        
        function gerarRelatorio() {
            const estagiarioId = document.getElementById('relatorio-estagiario').value;
            const dataInicio = document.getElementById('data-inicio').value;
            const dataFim = document.getElementById('data-fim').value;
            
            if (!dataInicio || !dataFim) {
                mostrarAlerta('Informe as datas inicial e final', 'error');
                return;
            }
            
            let registros = JSON.parse(localStorage.getItem('registros')) || [];
            
        
            if (estagiarioId) {
                registros = registros.filter(r => r.estagiarioId === estagiarioId);
            }
            
           
            registros = registros.filter(r => r.data >= dataInicio && r.data <= dataFim);
            
           
            registros.sort((a, b) => {
                if (a.data !== b.data) return a.data.localeCompare(b.data);
                return a.horaEntrada && b.horaEntrada ? a.horaEntrada.localeCompare(b.horaEntrada) : 0;
            });
            
            const tbody = document.querySelector('#tabela-relatorio tbody');
            tbody.innerHTML = '';
            
            if (registros.length === 0) {
                const tr = document.createElement('tr');
                tr.innerHTML = '<td colspan="6" style="text-align: center;">Nenhum registro encontrado.</td>';
                tbody.appendChild(tr);
                return;
            }
            
            const estagiarios = JSON.parse(localStorage.getItem('estagiarios')) || [];
            
            registros.forEach(registro => {
                const estagiario = estagiarios.find(e => e.id === registro.estagiarioId);
                const nomeEstagiario = estagiario ? estagiario.nome : 'Desconhecido';
                
              
                let horasTrabalhadas = '-';
                if (registro.horaEntrada && registro.horaSaida) {
                    const entrada = new Date(`2000-01-01T${registro.horaEntrada}`);
                    const saida = new Date(`2000-01-01T${registro.horaSaida}`);
                    const diff = (saida - entrada) / 1000 / 60; // diferença em minutos
                    
                    if (diff >= 0) {
                        const horas = Math.floor(diff / 60);
                        const minutos = Math.floor(diff % 60);
                        horasTrabalhadas = `${horas}h ${minutos}min`;
                    } else {
                        horasTrabalhadas = 'Inválido';
                    }
                }
                
                // Formatar data para exibição (DD/MM/AAAA)
                const dataParts = registro.data.split('-');
                const dataFormatada = `${dataParts[2]}/${dataParts[1]}/${dataParts[0]}`;
                
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${nomeEstagiario}</td>
                    <td>${dataFormatada}</td>
                    <td>${registro.horaEntrada || '-'}</td>
                    <td>${registro.horaSaida || '-'}</td>
                    <td>${horasTrabalhadas}</td>
                    <td>${registro.observacao || '-'}</td>
                `;
                tbody.appendChild(tr);
            });
        }
        
        function mostrarAlerta(mensagem, tipo) {
            const alert = document.getElementById('alert');
            alert.textContent = mensagem;
            alert.style.display = 'block';
            
            if (tipo === 'error') {
                alert.style.backgroundColor = '#f8d7da';
                alert.style.color = '#721c24';
            } else {
                alert.style.backgroundColor = '#d4edda';
                alert.style.color = '#155724';
            }
            
            setTimeout(() => {
                alert.style.display = 'none';
            }, 3000);
        }