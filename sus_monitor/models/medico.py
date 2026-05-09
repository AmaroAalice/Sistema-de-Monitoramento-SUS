from app.database import db

class Medico(db.Model):
    __tablename__ = "medicos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    especialidade = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "especialidade": self.especialidade,
            "telefone": self.telefone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
