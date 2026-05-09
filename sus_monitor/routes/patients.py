from flask import Blueprint, request, jsonify
from app.database import db
from models.patient import Paciente

patients_bp = Blueprint("patients", __name__)


@patients_bp.route("/", methods=["POST"])
def criar_paciente():
    dados = request.get_json() or {}
    nome = dados.get("nome")
    email = dados.get("email")
    telefone = dados.get("telefone")

    if not nome or not email:
        return jsonify({"erro": "nome e email são obrigatórios"}), 400

    paciente = Paciente(nome=nome, email=email, telefone=telefone)
    db.session.add(paciente)
    db.session.commit()

    return jsonify(paciente.to_dict()), 201


@patients_bp.route("/", methods=["GET"])
def listar_pacientes():
    pacientes = Paciente.query.all()
    return jsonify([paciente.to_dict() for paciente in pacientes]), 200
