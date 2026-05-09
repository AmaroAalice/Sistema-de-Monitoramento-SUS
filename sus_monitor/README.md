# SUS Monitor

Sistema de Monitoramento SUS simples usando Python, Flask e SQLite.

## Estrutura do projeto

- `app/`: código de inicialização do Flask, configuração e banco de dados.
- `models/`: classes do banco de dados (Paciente, Médico, Agendamento).
- `routes/`: rotas REST para pacientes e médicos.
- `instance/`: arquivo SQLite será criado aqui (`sus_monitor.db`).
- `run.py`: ponto de entrada para iniciar a aplicação.
- `requirements.txt`: dependências do projeto.

## Como rodar localmente

1. Abra um terminal dentro de `sus_monitor`.
2. Crie um ambiente virtual Python:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Instale as dependências:

```powershell
pip install -r requirements.txt
```

4. Inicie a aplicação:

```powershell
python run.py
```

A aplicação irá rodar em `http://127.0.0.1:5000`.

## Rotas disponíveis

- `POST /api/pacientes/` - criar paciente
- `GET /api/pacientes/` - listar pacientes
- `POST /api/medicos/` - criar médico
- `GET /api/medicos/` - listar médicos
- `GET /api/saude` - verificar se a API está funcionando

## Exemplo de requisição para criar paciente

```json
{
  "nome": "Ana Silva",
  "email": "ana@example.com",
  "telefone": "(11) 99999-9999"
}
```

## Observação

O banco de dados SQLite será criado automaticamente na primeira execução.
