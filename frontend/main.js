// JavaScript do dashboard do paciente que consome as APIs do backend.
const apiBase = '';
let unidadesCache = [];
let medicosCache = [];

const elementos = {
    unidadesContainer: document.getElementById('unidades-heatmap'),
    unidadeSelect: document.getElementById('unidade'),
    medicoSelect: document.getElementById('medico'),
    dataInput: document.getElementById('data'),
    horarioSelect: document.getElementById('horario'),
    formAgendamento: document.getElementById('form-agendamento'),
    sugestaoForm: document.getElementById('form-sugestao'),
    sugestaoMensagem: document.getElementById('sugestao-mensagem'),
    resultadoMensagem: document.getElementById('resultado-mensagem'),
    cidadeInput: document.getElementById('cidade'),
    latitudeInput: document.getElementById('latitude'),
    longitudeInput: document.getElementById('longitude'),
};

async function carregarUnidades() {
    const resposta = await fetch(`${apiBase}/api/unidades`);
    const dados = await resposta.json();
    if (!dados.success) {
        elementos.unidadesContainer.innerHTML = '<p>Falha ao carregar unidades.</p>';
        return;
    }
    unidadesCache = dados.unidades;
    renderizarHeatmap(unidadesCache);
    popularUnidadeSelect(unidadesCache);
}

function renderizarHeatmap(unidades) {
    elementos.unidadesContainer.innerHTML = unidades.map(unidade => {
        return `
            <article class="card" aria-labelledby="unidade-${unidade.id}-nome">
                <h3 id="unidade-${unidade.id}-nome">${unidade.nome}</h3>
                <p>${unidade.endereco}, ${unidade.cidade} - ${unidade.estado}</p>
                <p><strong>Ocupação:</strong> ${unidade.ocupacao_atual}/${unidade.capacidade} (${unidade.lotacao_percent}%)</p>
                <span class="status-pill status-${unidade.status_lotacao}">${unidade.status_lotacao.toUpperCase()}</span>
            </article>
        `;
    }).join('');
}

async function carregarMedicos() {
    const resposta = await fetch(`${apiBase}/api/medicos`);
    const dados = await resposta.json();
    if (!dados.success) {
        return;
    }
    medicosCache = dados.medicos;
    popularMedicoSelect();
}

function popularUnidadeSelect(unidades) {
    elementos.unidadeSelect.innerHTML = '<option value="">Selecione uma unidade</option>' + unidades.map(unidade => {
        return `<option value="${unidade.id}">${unidade.nome} - ${unidade.cidade}</option>`;
    }).join('');
}

function popularMedicoSelect() {
    const unidadeId = parseInt(elementos.unidadeSelect.value, 10);
    const medicosFiltrados = medicosCache.filter(medico => !unidadeId || medico.unidade_id === unidadeId);
    elementos.medicoSelect.innerHTML = '<option value="">Selecione um médico</option>' + medicosFiltrados.map(medico => {
        const unidade = unidadesCache.find(u => u.id === medico.unidade_id);
        const endereco = unidade ? `${unidade.nome}` : '';
        return `<option value="${medico.id}">${medico.nome} (${medico.especialidade}) - ${endereco}</option>`;
    }).join('');
    atualizarHorariosDisponiveis();
}

async function atualizarHorariosDisponiveis() {
    const medicoId = elementos.medicoSelect.value;
    const data = elementos.dataInput.value;
    elementos.horarioSelect.innerHTML = '<option value="">Selecione um horário</option>';
    if (!medicoId || !data) {
        return;
    }

    const resposta = await fetch(`${apiBase}/api/medicos/${medicoId}/horarios?data=${data}`);
    const dados = await resposta.json();
    if (!dados.success) {
        elementos.horarioSelect.innerHTML = '<option value="">Erro ao carregar horários</option>';
        return;
    }
    elementos.horarioSelect.innerHTML = '<option value="">Selecione um horário</option>' + dados.horarios_disponiveis.map(horario => `<option value="${horario}">${horario}</option>`).join('');
}

async function enviarAgendamento(event) {
    event.preventDefault();
    const unidadeId = parseInt(elementos.unidadeSelect.value, 10);
    const medicoId = parseInt(elementos.medicoSelect.value, 10);
    const data = elementos.dataInput.value;
    const horario = elementos.horarioSelect.value;

    if (!unidadeId || !medicoId || !data || !horario) {
        elementos.resultadoMensagem.textContent = 'Preencha todos os campos do agendamento.';
        elementos.resultadoMensagem.style.color = 'var(--vermelho)';
        return;
    }

    const dataHorario = `${data} ${horario}`;
    const payload = {
        usuario_id: 1,
        medico_id: medicoId,
        unidade_id: unidadeId,
        data_horario: dataHorario,
    };

    const resposta = await fetch(`${apiBase}/api/agendamentos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
    const dados = await resposta.json();
    if (dados.success) {
        elementos.resultadoMensagem.textContent = `Agendamento confirmado para ${dataHorario}.`; 
        elementos.resultadoMensagem.style.color = 'var(--verde)';
        carregarUnidades();
        atualizarHorariosDisponiveis();
    } else {
        elementos.resultadoMensagem.textContent = dados.erro || 'Erro ao agendar. Tente novamente.';
        elementos.resultadoMensagem.style.color = 'var(--vermelho)';
    }
}

async function enviarSugestao(event) {
    event.preventDefault();
    const latitude = elementos.latitudeInput.value;
    const longitude = elementos.longitudeInput.value;
    const cidade = elementos.cidadeInput.value.trim();

    const params = new URLSearchParams();
    if (latitude) params.append('latitude', latitude);
    if (longitude) params.append('longitude', longitude);
    if (cidade) params.append('cidade', cidade);

    const resposta = await fetch(`${apiBase}/api/unidade-mais-proxima?${params.toString()}`);
    const dados = await resposta.json();
    if (dados.success) {
        const unidade = dados.unidade_recomendada;
        elementos.sugestaoMensagem.innerHTML = `
            <strong>Unidade recomendada:</strong> ${unidade.nome}<br>
            Endereço: ${unidade.endereco}, ${unidade.cidade}<br>
            Status: <span class="status-pill status-${unidade.status_lotacao}">${unidade.status_lotacao.toUpperCase()}</span>
        `;
    } else {
        elementos.sugestaoMensagem.textContent = dados.erro || 'Não foi possível sugerir unidade.';
    }
}

function configurarEventos() {
    elementos.unidadeSelect.addEventListener('change', popularMedicoSelect);
    elementos.medicoSelect.addEventListener('change', atualizarHorariosDisponiveis);
    elementos.dataInput.addEventListener('change', atualizarHorariosDisponiveis);
    elementos.formAgendamento.addEventListener('submit', enviarAgendamento);
    elementos.sugestaoForm.addEventListener('submit', enviarSugestao);
}

function setarDataAtual() {
    const hoje = new Date();
    const isoData = hoje.toISOString().split('T')[0];
    elementos.dataInput.value = isoData;
}

window.addEventListener('DOMContentLoaded', async () => {
    carregarUnidades();
    carregarMedicos();
    setarDataAtual();
    configurarEventos();
});
