function registrarPresenca() {
      const nome = document.getElementById('nome').value.trim();
      const mensagem = document.getElementById('mensagem');
 
      if (nome === '') {
        mensagem.style.display = 'block';
        mensagem.className = 'mensagem faltou';
        mensagem.textContent = 'Por favor, digite seu nome.';
        return;
      }

      const agora = new Date();
      const horaAtual = agora.getHours();
      const minutos = agora.getMinutes().toString().padStart(2, '0');
      const horarioFormatado = `${horaAtual}:${minutos}`;
      const dataFormatada = agora.toLocaleDateString('pt-BR');
    
      if (horaAtual < 13) {
        mensagem.className = 'mensagem presente';
        mensagem.textContent = `✅ Presença registrada para ${nome} às ${horarioFormatado} - ${dataFormatada}`;
      } else {
        mensagem.className = 'mensagem faltou';
        mensagem.textContent = `❌ Registro após o horário! ${nome} foi marcado como FALTOU - ${dataFormatada} às ${horarioFormatado}`;
      }

      mensagem.style.display = 'block';
    }