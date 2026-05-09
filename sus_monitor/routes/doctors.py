from flask import Blueprint, request, jsonify
from app.database import db
from models.doctor import Medico


doctors_bp = Blueprint("doctors", __name__)


@doctors_bp.route("/", methods=["POST"])
def criar_medico():
    dados = request.get_json() or {}
    nome = dados.get("nome")
    especialidade = dados.get("especialidade")
    telefone = dados.get("telefone")

    if not nome or not especialidade:
        return jsonify({"erro": "nome e especialidade são obrigatórios"}), 400

    medico = Medico(nome=nome, especialidade=especialidade, telefone=telefone)
    db.session.add(medico)
    db.session.commit()

    return jsonify(medico.to_dict()), 201


@doctors_bp.route("/", methods=["GET"])
def listar_medicos():
    medicos = Medico.query.all()
    return jsonify([medico.to_dict() for medico in medicos]), 200
