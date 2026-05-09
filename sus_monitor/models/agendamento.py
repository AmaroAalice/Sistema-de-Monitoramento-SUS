from app.database import db

class Agendamento(db.Model):
    __tablename__ = "agendamentos"

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey("pacientes.id"), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey("medicos.id"), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.String(30), nullable=False, default="agendado")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    paciente = db.relationship("Paciente")
    medico = db.relationship("Medico")

    def to_dict(self):
        return {
            "id": self.id,
            "paciente": self.paciente.to_dict() if self.paciente else None,
            "medico": self.medico.to_dict() if self.medico else None,
            "data_hora": self.data_hora.isoformat(),
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
