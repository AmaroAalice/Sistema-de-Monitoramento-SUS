from app.database import db


class Agendamento(db.Model):
    __tablename__ = "agendamentos"

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey("pacientes.id"), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey("medicos.id"), nullable=False)
    horario = db.Column(db.String(10), nullable=False)
    data = db.Column(db.String(10), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "paciente_id": self.paciente_id,
            "medico_id": self.medico_id,
            "data": self.data,
            "horario": self.horario,
        }
