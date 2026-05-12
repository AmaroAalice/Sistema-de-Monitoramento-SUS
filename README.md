# Plataforma de Monitoramento SUS

## Como rodar o projeto completo

### 1. Abrir o terminal na pasta do projeto
Abra o **PowerShell** ou **Prompt de Comando** em:

`c:\Users\99849285\Documents\Monitoriamento sus`

### 2. Ativar o ambiente virtual
Se você já tiver o ambiente virtual criado, execute:

```powershell
.\.venv\Scripts\Activate
```

Se não existir `.venv`, crie um ambiente e instale as dependências:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate
pip install -r backend\requirements.txt
```

### 3. Instalar dependências (se necessário)

```powershell
pip install -r backend\requirements.txt
```

### 4. Executar o backend Flask

Use o módulo Python para iniciar o aplicativo dentro do pacote:

```powershell
python -m backend.app
```

O servidor irá subir em `http://127.0.0.1:5000`

### 5. Abrir o frontend no navegador
- Dashboard do paciente: `http://127.0.0.1:5000/`
- Painel administrativo: `http://127.0.0.1:5000/admin`

### 6. Funcionalidades disponíveis
- Listar unidades e status de lotação
- Buscar horários disponíveis por médico
- Criar agendamento remoto
- Sugerir unidade mais próxima
- Atualizar status de lotação no painel administrativo

### Observações
- O backend usa banco SQLite em `backend/database.db`
- Os arquivos estáticos ficam em `frontend/`
- O `README` ajuda a executar o projeto completo durante sua apresentação
