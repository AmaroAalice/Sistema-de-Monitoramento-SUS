from datetime import datetime
from flask import current_app
from sqlalchemy import event

from backend import db

# Definição das tabelas do banco de dados usando SQLAlchemy.

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    telefone = db.Column(db.String(30), nullable=True)
    tipo = db.Column(db.String(20), nullable=False, default='paciente')
    senha_hash = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'tipo': self.tipo,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

class Unidade(db.Model):
    __tablename__ = 'unidades'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    endereco = db.Column(db.String(300), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    status_lotacao = db.Column(db.String(20), nullable=False, default='verde')
    capacidade = db.Column(db.Integer, nullable=False, default=100)
    ocupacao_atual = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    medicos = db.relationship('Medico', backref='unidade', lazy=True)
    agendamentos = db.relationship('Agendamento', backref='unidade', lazy=True)
    logs_fluxo = db.relationship('LogFluxo', backref='unidade', lazy=True)

    def lotacao_percent(self):
        if self.capacidade <= 0:
            return 0
        return min(100, round((self.ocupacao_atual / self.capacidade) * 100))

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'endereco': self.endereco,
            'cidade': self.cidade,
            'estado': self.estado,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'status_lotacao': self.status_lotacao,
            'capacidade': self.capacidade,
            'ocupacao_atual': self.ocupacao_atual,
            'lotacao_percent': self.lotacao_percent(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

class Medico(db.Model):
    __tablename__ = 'medicos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    especialidade = db.Column(db.String(150), nullable=False)
    unidade_id = db.Column(db.Integer, db.ForeignKey('unidades.id'), nullable=False)
    horario_atendimento = db.Column(db.JSON, nullable=False, default=[])
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    agendamentos = db.relationship('Agendamento', backref='medico', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'especialidade': self.especialidade,
            'unidade_id': self.unidade_id,
            'horario_atendimento': self.horario_atendimento,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

class Agendamento(db.Model):
    __tablename__ = 'agendamentos'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=False)
    unidade_id = db.Column(db.Integer, db.ForeignKey('unidades.id'), nullable=False)
    data_horario = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='confirmado')
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    usuario = db.relationship('Usuario', backref='agendamentos')

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'medico_id': self.medico_id,
            'unidade_id': self.unidade_id,
            'data_horario': self.data_horario.isoformat(),
            'status': self.status,
            'criado_em': self.criado_em.isoformat(),
            'atualizado_em': self.atualizado_em.isoformat(),
        }

class LogFluxo(db.Model):
    __tablename__ = 'logs_fluxo'

    id = db.Column(db.Integer, primary_key=True)
    unidade_id = db.Column(db.Integer, db.ForeignKey('unidades.id'), nullable=False)
    nivel_fluxo = db.Column(db.String(20), nullable=False)
    quantidade_pessoas = db.Column(db.Integer, nullable=False, default=0)
    registro_em = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    descricao = db.Column(db.String(300), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'unidade_id': self.unidade_id,
            'nivel_fluxo': self.nivel_fluxo,
            'quantidade_pessoas': self.quantidade_pessoas,
            'registro_em': self.registro_em.isoformat(),
            'descricao': self.descricao,
        }

# Cria dados iniciais de exemplo quando o banco é inicializado pela primeira vez.

def init_db(app):
    with app.app_context():
        db.create_all()

        # Se já existirem unidades cadastradas, não inserimos dados de exemplo.
        if Unidade.query.first():
            return

        unidade1 = Unidade(
            nome='UBS Central',
            endereco='Rua das Flores, 123',
            cidade='São Paulo',
            estado='SP',
            latitude=-23.55052,
            longitude=-46.63331,
            status_lotacao='amarelo',
            capacidade=120,
            ocupacao_atual=78,
        )
        unidade2 = Unidade(
            nome='Policlínica Norte',
            endereco='Av. Brasil, 456',
            cidade='São Paulo',
            estado='SP',
            latitude=-23.52000,
            longitude=-46.62000,
            status_lotacao='verde',
            capacidade=90,
            ocupacao_atual=34,
        )
        unidade3 = Unidade(
            nome='UPA Sul',
            endereco='Travessa Santa Maria, 89',
            cidade='São Paulo',
            estado='SP',
            latitude=-23.56000,
            longitude=-46.64000,
            status_lotacao='vermelho',
            capacidade=100,
            ocupacao_atual=99,
        )

        medico1 = Medico(
            nome='Dra. Ana Souza',
            especialidade='Clínico Geral',
            unidade=unidade1,
            horario_atendimento=['08:00', '09:00', '10:00', '11:00', '13:00', '14:00'],
        )
        medico2 = Medico(
            nome='Dr. Carlos Oliveira',
            especialidade='Pediatria',
            unidade=unidade2,
            horario_atendimento=['09:00', '10:00', '11:00', '14:00', '15:00'],
        )
        medico3 = Medico(
            nome='Dra. Fernanda Lima',
            especialidade='Ginecologia',
            unidade=unidade3,
            horario_atendimento=['08:30', '09:30', '10:30', '13:30', '14:30'],
        )

        paciente = Usuario(
            nome='João da Silva',
            email='joao.silva@example.com',
            telefone='(11) 98765-4321',
            tipo='paciente',
        )
        funcionario = Usuario(
            nome='Maria Fernandes',
            email='maria.fernandes@example.com',
            telefone='(11) 91234-5678',
            tipo='funcionario',
        )

        db.session.add_all([unidade1, unidade2, unidade3, medico1, medico2, medico3, paciente, funcionario])
        db.session.commit()

        log_example = LogFluxo(
            unidade=unidade1,
            nivel_fluxo='amarelo',
            quantidade_pessoas=78,
            descricao='Atualização inicial de fluxo para demonstrar o heatmap.',
        )
        db.session.add(log_example)
        db.session.commit()

# Atualiza automaticamente a data de modificação ao alterar registros de Unidade.

@event.listens_for(Unidade, 'before_update')
def receber_before_update(mapper, connection, target):
    target.updated_at = datetime.utcnow()
