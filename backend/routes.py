from datetime import datetime, date
import math

from flask import Blueprint, current_app, jsonify, request

from backend import db
from backend.models import Agendamento, LogFluxo, Medico, Unidade, Usuario

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Função auxiliar para calcular distância entre coordenadas geográficas.

def calcular_distancia(lat1, lon1, lat2, lon2):
    # Fórmula de Haversine simples, usada aqui de maneira fictícia para ranking de unidades.
    raio_terra = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return raio_terra * c

# Rota para listar unidades com status de lotação e informações de heatmap.

@api_bp.route('/unidades', methods=['GET'])
def listar_unidades():
    unidades = Unidade.query.order_by(Unidade.nome).all()
    resultado = [u.to_dict() for u in unidades]
    return jsonify({'success': True, 'unidades': resultado})

# Rota para obter horários disponíveis de um médico específico.

@api_bp.route('/medicos/<int:medico_id>/horarios', methods=['GET'])
def obter_horarios_medico(medico_id):
    medico = Medico.query.get(medico_id)
    if not medico:
        return jsonify({'success': False, 'erro': 'Médico não encontrado.'}), 404

    data_str = request.args.get('data')
    if data_str:
        try:
            data_referencia = datetime.strptime(data_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'erro': 'Formato de data inválido. Use YYYY-MM-DD.'}), 400
    else:
        data_referencia = date.today()

    # Coleta horários já agendados para este médico na data informada.
    agendamentos_existentes = Agendamento.query.filter(
        Agendamento.medico_id == medico_id,
        db.func.date(Agendamento.data_horario) == data_referencia,
        Agendamento.status == 'confirmado'
    ).all()

    horarios_reservados = {agendamento.data_horario.strftime('%H:%M') for agendamento in agendamentos_existentes}
    horarios_disponiveis = [hora for hora in medico.horario_atendimento if hora not in horarios_reservados]

    return jsonify({
        'success': True,
        'medico': medico.to_dict(),
        'data': data_referencia.isoformat(),
        'horarios_disponiveis': horarios_disponiveis,
    })

# Rota para listar médicos, opcionalmente filtrando por unidade.

@api_bp.route('/medicos', methods=['GET'])
def listar_medicos():
    unidade_id = request.args.get('unidade_id', type=int)
    consulta = Medico.query
    if unidade_id:
        consulta = consulta.filter(Medico.unidade_id == unidade_id)

    medicos = consulta.order_by(Medico.nome).all()
    return jsonify({
        'success': True,
        'medicos': [medico.to_dict() for medico in medicos],
    })

# Rota para criar um novo agendamento.

@api_bp.route('/agendamentos', methods=['POST'])
def criar_agendamento():
    dados = request.get_json() or {}
    usuario_id = dados.get('usuario_id')
    medico_id = dados.get('medico_id')
    unidade_id = dados.get('unidade_id')
    data_horario_str = dados.get('data_horario')

    if not usuario_id or not medico_id or not unidade_id or not data_horario_str:
        return jsonify({'success': False, 'erro': 'usuario_id, medico_id, unidade_id e data_horario são obrigatórios.'}), 400

    usuario = Usuario.query.get(usuario_id)
    medico = Medico.query.get(medico_id)
    unidade = Unidade.query.get(unidade_id)

    if not usuario:
        return jsonify({'success': False, 'erro': 'Usuário não encontrado.'}), 404
    if not medico:
        return jsonify({'success': False, 'erro': 'Médico não encontrado.'}), 404
    if not unidade:
        return jsonify({'success': False, 'erro': 'Unidade não encontrada.'}), 404
    if medico.unidade_id != unidade.id:
        return jsonify({'success': False, 'erro': 'O médico não atende na unidade selecionada.'}), 400

    try:
        if 'T' in data_horario_str:
            data_horario = datetime.fromisoformat(data_horario_str)
        else:
            data_horario = datetime.strptime(data_horario_str, '%Y-%m-%d %H:%M')
    except ValueError:
        return jsonify({'success': False, 'erro': 'Formato de data_horario inválido. Use YYYY-MM-DD HH:MM ou ISO 8601.'}), 400

    horario_string = data_horario.strftime('%H:%M')
    if horario_string not in medico.horario_atendimento:
        return jsonify({'success': False, 'erro': 'Horário indisponível para este médico.'}), 400

    agendamento_existente = Agendamento.query.filter(
        Agendamento.medico_id == medico_id,
        Agendamento.data_horario == data_horario,
        Agendamento.status == 'confirmado'
    ).first()
    if agendamento_existente:
        return jsonify({'success': False, 'erro': 'Horário já foi reservado.'}), 409

    agendamento = Agendamento(
        usuario_id=usuario.id,
        medico_id=medico.id,
        unidade_id=unidade.id,
        data_horario=data_horario,
        status='confirmado',
    )
    db.session.add(agendamento)

    # Atualiza a ocupação da unidade e registra um log de fluxo.
    unidade.ocupacao_atual = min(unidade.capacidade, unidade.ocupacao_atual + 1)
    descricao = f'Agendamento criado para {usuario.nome} com {medico.nome} em {data_horario.strftime("%d/%m/%Y %H:%M")}.'
    log_fluxo = LogFluxo(
        unidade_id=unidade.id,
        nivel_fluxo=unidade.status_lotacao,
        quantidade_pessoas=unidade.ocupacao_atual,
        descricao=descricao,
    )
    db.session.add(log_fluxo)
    db.session.commit()

    return jsonify({'success': True, 'agendamento': agendamento.to_dict()}), 201

# Rota para sugerir a unidade mais próxima com base em coordenadas e lotação.

@api_bp.route('/unidade-mais-proxima', methods=['GET'])
def sugerir_unidade_mais_proxima():
    latitude = request.args.get('latitude', type=float)
    longitude = request.args.get('longitude', type=float)
    cidade = request.args.get('cidade')

    unidades = Unidade.query.all()
    if not unidades:
        return jsonify({'success': False, 'erro': 'Nenhuma unidade cadastrada.'}), 404

    candidatos = unidades
    if cidade:
        candidatos = [u for u in unidades if u.cidade.lower() == cidade.lower()]
        if not candidatos:
            candidatos = unidades

    if latitude is None or longitude is None:
        # Se coordenadas não forem enviadas, escolhe a primeira unidade na cidade desejada ou a de menor lotação.
        candidatos = sorted(candidatos, key=lambda u: ('verde', 'amarelo', 'vermelho').index(u.status_lotacao))
        unidade_selecionada = candidatos[0]
    else:
        # Ordena por distância e preferência de lotação.
        for unidade in candidatos:
            unidade.distancia = calcular_distancia(latitude, longitude, unidade.latitude, unidade.longitude)
            status_rank = {'verde': 0, 'amarelo': 1, 'vermelho': 2}.get(unidade.status_lotacao, 3)
            unidade.peso = unidade.distancia + status_rank * 5
        unidade_selecionada = sorted(candidatos, key=lambda u: (u.peso, u.distancia))[0]

    return jsonify({
        'success': True,
        'unidade_recomendada': unidade_selecionada.to_dict(),
        'criterios': {
            'latitude': latitude,
            'longitude': longitude,
            'cidade': cidade,
        }
    })

# Rota administrativa para alterar o status de lotação de uma unidade.

@api_bp.route('/unidades/<int:unidade_id>/status', methods=['PUT'])
def atualizar_status_unidade(unidade_id):
    dados = request.get_json() or {}
    novo_status = dados.get('status_lotacao')
    ocupacao_atual = dados.get('ocupacao_atual')

    if novo_status not in ('verde', 'amarelo', 'vermelho'):
        return jsonify({'success': False, 'erro': 'status_lotacao deve ser verde, amarelo ou vermelho.'}), 400

    unidade = Unidade.query.get(unidade_id)
    if not unidade:
        return jsonify({'success': False, 'erro': 'Unidade não encontrada.'}), 404

    unidade.status_lotacao = novo_status
    if isinstance(ocupacao_atual, int):
        unidade.ocupacao_atual = max(0, min(unidade.capacidade, ocupacao_atual))

    descricao = f'Status de lotação alterado para {novo_status}.'
    log_fluxo = LogFluxo(
        unidade_id=unidade.id,
        nivel_fluxo=novo_status,
        quantidade_pessoas=unidade.ocupacao_atual,
        descricao=descricao,
    )
    db.session.add(log_fluxo)
    db.session.commit()

    return jsonify({'success': True, 'unidade': unidade.to_dict()})