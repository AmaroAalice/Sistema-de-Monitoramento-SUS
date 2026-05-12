# Arquitetura do Projeto: Plataforma de Otimização do Atendimento no SUS

## 1. Visão Geral do Sistema

A plataforma será um sistema web para monitoramento de fluxo de atendimento em unidades de saúde e agendamento remoto. O objetivo é reduzir o tempo de espera, melhorar a distribuição dos pacientes e permitir que funcionários da unidade gerenciem a ocupação em tempo real.

## 2. Requisitos Funcionais

### 2.1 Usuário Paciente
- Visualizar lista de unidades de saúde disponíveis.
- Consultar o status de lotação de cada unidade em sinalização de semáforo:
  - Verde: fluxo normal
  - Amarelo: fluxo alto
  - Vermelho: lotado
- Buscar horários disponíveis de um médico específico.
- Realizar agendamento remoto.
- Receber sugestão da unidade mais próxima com base em geolocalização fictícia.
- Acessar um dashboard responsivo com painel de movimentação (heatmap) e formulário de agendamento.

### 2.2 Funcionário da Unidade
- Alterar manualmente o status de lotação da unidade.
- Visualizar os agendamentos da unidade (futura etapa; inicialmente foco no status e heatmap).

### 2.3 Administrador / Sistema
- Registrar usuários, médicos e unidades.
- Registrar logs de fluxo para análises e auditoria.
- Oferecer API REST para consumo do frontend.

## 3. Requisitos Não Funcionais

- Backend em Python com Flask.
- Banco de dados relacional (pode ser SQLite no protótipo, PostgreSQL em produção).
- Frontend responsivo com foco em acessibilidade e identidade visual SUS (azul, branco, contrastes altos).
- Comentários exaustivos no código para apresentação acadêmica.
- Arquitetura simples e modular, permitindo expansão futura.
- Segurança básica: validação de entrada e tratamento de erros.
- Usabilidade: formulários com labels claros, navegação por teclado e contraste de cores adequado.

## 4. Proposta de Modelo de Dados Relacional

### 4.1 Tabelas Principais

#### Usuarios
- `id` (PK, inteiro, auto incremental)
- `nome` (texto)
- `email` (texto, único)
- `telefone` (texto)
- `tipo` (texto: `paciente`, `funcionario`, `admin`)
- `senha_hash` (texto)
- `created_at` (timestamp)
- `updated_at` (timestamp)

#### Medicos
- `id` (PK, inteiro, auto incremental)
- `nome` (texto)
- `especialidade` (texto)
- `unidade_id` (FK para Unidades)
- `horario_atendimento` (texto ou JSON com faixas de horário)
- `created_at` (timestamp)
- `updated_at` (timestamp)

#### Unidades
- `id` (PK, inteiro, auto incremental)
- `nome` (texto)
- `endereco` (texto)
- `cidade` (texto)
- `estado` (texto)
- `latitude` (decimal)
- `longitude` (decimal)
- `status_lotacao` (texto: `verde`, `amarelo`, `vermelho`)
- `capacidade` (inteiro)
- `ocupacao_atual` (inteiro)
- `created_at` (timestamp)
- `updated_at` (timestamp)

#### Agendamentos
- `id` (PK, inteiro, auto incremental)
- `usuario_id` (FK para Usuarios)
- `medico_id` (FK para Medicos)
- `unidade_id` (FK para Unidades)
- `data_horario` (timestamp)
- `status` (texto: `confirmado`, `cancelado`, `pendente`)
- `criado_em` (timestamp)
- `atualizado_em` (timestamp)

#### LogsFluxo
- `id` (PK, inteiro, auto incremental)
- `unidade_id` (FK para Unidades)
- `nivel_fluxo` (texto: `verde`, `amarelo`, `vermelho`)
- `quantidade_pessoas` (inteiro)
- `registro_em` (timestamp)
- `descricao` (texto)

## 5. Fluxos Principais de Uso

### 5.1 Consulta de Unidades e Lotação
1. O paciente acessa o dashboard.
2. O frontend chama a API para listar unidades e seus status.
3. O backend retorna unidades com cálculo de lotação simplificado.
4. O frontend apresenta as unidades com indicadores de semáforo.

### 5.2 Busca de Horários de Médico
1. O paciente escolhe um médico ou unidade.
2. O frontend solicita à API os horários disponíveis.
3. O backend consulta `Medicos` e retorna horários livres.
4. O paciente escolhe um horário para agendar.

### 5.3 Agendamento Remoto
1. O paciente envia pedido de agendamento.
2. O backend valida `usuario_id`, `medico_id`, `unidade_id` e horário.
3. O backend cria registro em `Agendamentos` com status `confirmado`.
4. O frontend exibe confirmação e dados do agendamento.

### 5.4 Sugestão de Unidade Mais Próxima
1. O paciente informa um ponto de referência fictício (latitude/longitude ou cidade).
2. O backend aplica lógica de geolocalização fictícia.
3. O sistema sugere a unidade mais próxima com menor status de lotação.

### 5.5 Painel Administrativo
1. Funcionário faz login (ou acessa via interface simples).
2. Escolhe a unidade.
3. Atualiza `status_lotacao` para `verde`, `amarelo` ou `vermelho`.
4. O backend registra alteração e atualiza `LogsFluxo`.

## 6. Proposta de Estrutura de Pastas

- `/docs` - documentação do projeto
- `/backend` - código Flask, rotas e modelo de dados
- `/frontend` - interface do usuário, HTML/CSS/JS ou React
- `/backend/app.py` - entrada da API Flask
- `/backend/models.py` - definição de modelos e esquema de banco
- `/backend/routes.py` - rotas de API e lógica
- `/frontend/index.html` - dashboard do paciente
- `/frontend/admin.html` - painel administrativo

## 7. Observações Técnicas

- Usar SQLite para protótipo simplificado e facilitar testes locais.
- Incluir comentários no backend e frontend explicando cada bloco.
- Adotar HTML semântico e ARIA para acessibilidade.
- Preferir CSS simples com cores SUS: azul (`#004aad`, `#0077cc`) e branco, e ícones/símbolos de semáforo.
- Modelar dados pensando em futuras integrações com sistemas de prontuário e APIs de geolocalização reais.

## 8. Próximos Passos
1. Criar a base do backend em Python/Flask.
2. Implementar rotas: listar unidades, buscar horários, agendar, sugerir unidade.
3. Criar frontend responsivo com dashboard de paciente e painel administrativo.
4. Testar fluxo de agendamento e alteração de status.

---

> Esta documentação inicial define o escopo técnico e o modelo relacional para a plataforma SUS de monitoramento de fluxo e agendamento remoto.
