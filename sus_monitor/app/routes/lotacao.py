from datetime import datetime
from flask import Blueprint, request, jsonify
from models.agendamento import Agendamento

bp_lotacao = Blueprint("lotacao", __name__)

def status_por_fluxo(contagem):
    if contagem <= 2:
        return "verde"
    if contagem <= 4:
        return "amarelo"
    return "vermelho"

@bp_lotacao.route("/", methods=["GET"])
def ver_lotacao():
    data_texto = request.args.get("data")
    if not data_texto:
        return jsonify({"erro": "data é obrigatória"}), 400

    try:
        data = datetime.fromisoformat(data_texto).date()
    except ValueError:
        return jsonify({"erro": "data inválida"}), 400

    painel = []
    for hora in range(7, 19):
        data_hora = datetime.combine(data, datetime.min.time()).replace(hour=hora)
        contagem = Agendamento.query.filter_by(data_hora=data_hora).count()
        
        painel.append({
            "hora": data_hora.strftime("%H:%M"),
            "agendamentos": contagem,
            "status": status_por_fluxo(contagem),
        })

    return jsonify({"data": data.isoformat(), "painel": painel}), 200
