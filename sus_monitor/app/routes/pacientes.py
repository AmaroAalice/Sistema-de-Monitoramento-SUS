from flask import Blueprint, request, jsonify
from app.database import db
from models.paciente import Paciente

bp_pacientes = Blueprint("pacientes", __name__)

@bp_pacientes.route("/", methods=["POST"])
def criar_paciente():
    data = request.get_json() or {}
    nome = data.get("nome")
    email = data.get("email")
    telefone = data.get("telefone")

    if not nome or not email or not telefone:
        return jsonify({"erro": "nome, email e telefone são obrigatórios"}), 400

    paciente_existe = Paciente.query.filter_by(email=email).first()
    if paciente_existe:
        return jsonify({"erro": "Email já cadastrado"}), 400

    paciente = Paciente(nome=nome, email=email, telefone=telefone)
    db.session.add(paciente)
    db.session.commit()

    return jsonify(paciente.to_dict()), 201

@bp_pacientes.route("/", methods=["GET"])
def listar_pacientes():
    pacientes = Paciente.query.order_by(Paciente.nome).all()
    return jsonify([paciente.to_dict() for paciente in pacientes]), 200

@bp_pacientes.route("/<int:paciente_id>", methods=["GET"])
def obter_paciente(paciente_id):
    paciente = Paciente.query.get(paciente_id)
    if not paciente:
        return jsonify({"erro": "Paciente não encontrado"}), 404
    return jsonify(paciente.to_dict()), 200
