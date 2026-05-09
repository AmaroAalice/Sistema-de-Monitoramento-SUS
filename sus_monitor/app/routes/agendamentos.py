from datetime import datetime
from flask import Blueprint, request, jsonify
from app.database import db
from models.agendamento import Agendamento
from models.paciente import Paciente
from models.medico import Medico

bp_agendamentos = Blueprint("agendamentos", __name__)

def valida_horario(data_hora):
    if data_hora.minute != 0 or data_hora.second != 0 or data_hora.microsecond != 0:
        return False
    return 7 <= data_hora.hour < 19

@bp_agendamentos.route("/", methods=["POST"])
def criar_agendamento():
    data = request.get_json() or {}
    paciente_id = data.get("paciente_id")
    medico_id = data.get("medico_id")
    data_hora_texto = data.get("data_hora")

    if not paciente_id or not medico_id or not data_hora_texto:
        return jsonify({"erro": "paciente_id, medico_id e data_hora são obrigatórios"}), 400

    paciente = Paciente.query.get(paciente_id)
    medico = Medico.query.get(medico_id)
    if not paciente or not medico:
        return jsonify({"erro": "paciente_id ou medico_id inválido"}), 404

    try:
        data_hora = datetime.fromisoformat(data_hora_texto)
    except ValueError:
        return jsonify({"erro": "data_hora deve estar em formato ISO 8601"}), 400

    if not valida_horario(data_hora):
        return jsonify({"erro": "Horário inválido. Somente horários inteiros entre 07:00 e 18:00"}), 400

    conflito = Agendamento.query.filter_by(medico_id=medico_id, data_hora=data_hora).first()
    if conflito:
        return jsonify({"erro": "Horário já reservado"}), 400

    agendamento = Agendamento(paciente_id=paciente_id, medico_id=medico_id, data_hora=data_hora)
    db.session.add(agendamento)
    db.session.commit()

    return jsonify(agendamento.to_dict()), 201

@bp_agendamentos.route("/", methods=["GET"])
def listar_agendamentos():
    agendamentos = Agendamento.query.order_by(Agendamento.data_hora).all()
    return jsonify([agendamento.to_dict() for agendamento in agendamentos]), 200

@bp_agendamentos.route("/<int:agendamento_id>", methods=["GET"])
def obter_agendamento(agendamento_id):
    agendamento = Agendamento.query.get(agendamento_id)
    if not agendamento:
        return jsonify({"erro": "Agendamento não encontrado"}), 404
    return jsonify(agendamento.to_dict()), 200

@bp_agendamentos.route("/disponiveis", methods=["GET"])
def horarios_disponiveis():
    data_texto = request.args.get("data")
    medico_id = request.args.get("medico_id", type=int)

    if not data_texto:
        return jsonify({"erro": "data é obrigatória"}), 400

    try:
        data = datetime.fromisoformat(data_texto).date()
    except ValueError:
        return jsonify({"erro": "data inválida"}), 400

    slots = []
    for hora in range(7, 19):
        data_hora = datetime.combine(data, datetime.min.time()).replace(hour=hora)
        query = Agendamento.query.filter_by(data_hora=data_hora)
        if medico_id:
            query = query.filter_by(medico_id=medico_id)

        if query.first() is None:
            slots.append(data_hora.strftime("%H:%M"))

    return jsonify({"data": data.isoformat(), "medico_id": medico_id, "horarios_disponiveis": slots}), 200
