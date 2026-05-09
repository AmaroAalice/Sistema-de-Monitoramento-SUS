from app.database import db


class Medico(db.Model):
    __tablename__ = "medicos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    especialidade = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "especialidade": self.especialidade,
            "telefone": self.telefone,
        }
