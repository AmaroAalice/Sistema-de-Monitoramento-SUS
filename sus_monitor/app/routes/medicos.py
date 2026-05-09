from flask import Blueprint, request, jsonify
from app.database import db
from models.medico import Medico

bp_medicos = Blueprint("medicos", __name__)

@bp_medicos.route("/", methods=["POST"])
def criar_medico():
    data = request.get_json() or {}
    nome = data.get("nome")
    especialidade = data.get("especialidade")
    telefone = data.get("telefone")

    if not nome or not especialidade or not telefone:
        return jsonify({"erro": "nome, especialidade e telefone são obrigatórios"}), 400

    medico = Medico(nome=nome, especialidade=especialidade, telefone=telefone)
    db.session.add(medico)
    db.session.commit()

    return jsonify(medico.to_dict()), 201

@bp_medicos.route("/", methods=["GET"])
def listar_medicos():
    medicos = Medico.query.order_by(Medico.nome).all()
    return jsonify([medico.to_dict() for medico in medicos]), 200

@bp_medicos.route("/<int:medico_id>", methods=["GET"])
def obter_medico(medico_id):
    medico = Medico.query.get(medico_id)
    if not medico:
        return jsonify({"erro": "Médico não encontrado"}), 404
    return jsonify(medico.to_dict()), 200
