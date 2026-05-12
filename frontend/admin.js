// JavaScript do painel administrativo para atualizar o status de lotação das unidades.
const adminElements = {
    unidadesLista: document.getElementById('admin-unidades'),
    unidadeSelect: document.getElementById('admin-unidade'),
    statusRadios: document.querySelectorAll('input[name="status_lotacao"]'),
    ocupacaoInput: document.getElementById('ocupacao_atual'),
    formStatus: document.getElementById('form-status'),
    alertaAdmin: document.getElementById('alerta-admin'),
};

let unidadesAdminCache = [];

async function carregarUnidadesAdmin() {
    const resposta = await fetch('/api/unidades');
    const dados = await resposta.json();
    if (!dados.success) {
        adminElements.unidadesLista.textContent = 'Erro ao carregar unidades.';
        return;
    }
    unidadesAdminCache = dados.unidades;
    renderizarUnidadesAdmin();
    popularUnidadeAdmin();
}

function renderizarUnidadesAdmin() {
    adminElements.unidadesLista.innerHTML = unidadesAdminCache.map(unidade => {
        return `
            <li>
                <strong>${unidade.nome}</strong> - ${unidade.endereco} <br>
                Status: <span class="status-pill status-${unidade.status_lotacao}">${unidade.status_lotacao.toUpperCase()}</span>
                | Ocupação: ${unidade.ocupacao_atual}/${unidade.capacidade}
            </li>
        `;
    }).join('');
}

function popularUnidadeAdmin() {
    adminElements.unidadeSelect.innerHTML = unidadesAdminCache.map(unidade => {
        return `<option value="${unidade.id}">${unidade.nome}</option>`;
    }).join('');
    atualizarFormularioAdmin();
}

function atualizarFormularioAdmin() {
    const unidadeId = parseInt(adminElements.unidadeSelect.value, 10);
    const unidade = unidadesAdminCache.find(u => u.id === unidadeId);
    if (!unidade) return;

    adminElements.ocupacaoInput.value = unidade.ocupacao_atual;
    adminElements.statusRadios.forEach(radio => {
        radio.checked = radio.value === unidade.status_lotacao;
    });
}

async function enviarStatusAdmin(event) {
    event.preventDefault();
    const unidadeId = parseInt(adminElements.unidadeSelect.value, 10);
    const statusSelecionado = Array.from(adminElements.statusRadios).find(r => r.checked)?.value;
    const ocupacao = parseInt(adminElements.ocupacaoInput.value, 10);

    if (!statusSelecionado || Number.isNaN(ocupacao)) {
        adminElements.alertaAdmin.textContent = 'Preencha o status e a ocupação corretamente.';
        return;
    }

    const resposta = await fetch(`/api/unidades/${unidadeId}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status_lotacao: statusSelecionado, ocupacao_atual: ocupacao }),
    });
    const dados = await resposta.json();
    if (dados.success) {
        adminElements.alertaAdmin.textContent = 'Status atualizado com sucesso.';
        carregarUnidadesAdmin();
    } else {
        adminElements.alertaAdmin.textContent = dados.erro || 'Erro ao atualizar status.';
    }
}

window.addEventListener('DOMContentLoaded', () => {
    carregarUnidadesAdmin();
    adminElements.unidadeSelect.addEventListener('change', atualizarFormularioAdmin);
    adminElements.formStatus.addEventListener('submit', enviarStatusAdmin);
});
