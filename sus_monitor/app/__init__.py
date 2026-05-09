from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sus_monitor.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "sus-monitor-dev-key-2024"
    app.config["JSON_SORT_KEYS"] = False

    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from app.routes.pacientes    import bp_pacientes
    from app.routes.medicos      import bp_medicos
    from app.routes.agendamentos import bp_agendamentos
    from app.routes.lotacao      import bp_lotacao
    from app.routes.auth         import bp_auth

    app.register_blueprint(bp_auth,         url_prefix="/api")
    app.register_blueprint(bp_pacientes,    url_prefix="/api")
    app.register_blueprint(bp_medicos,      url_prefix="/api")
    app.register_blueprint(bp_agendamentos, url_prefix="/api")
    app.register_blueprint(bp_lotacao,      url_prefix="/api")

    with app.app_context():
        db.create_all()
        _seed_admin()

    return app


def _seed_admin():
    """Cria usuários padrão se não existirem."""
    from app.models.usuario import Usuario
    if not Usuario.query.filter_by(email="admin@sus.gov.br").first():
        for nome, email, senha, perfil in [
            ("Administrador",      "admin@sus.gov.br",    "admin123",    Usuario.PERFIL_ADMIN),
            ("Recepcionista Demo", "recepcao@sus.gov.br", "recepcao123", Usuario.PERFIL_RECEPCIONISTA),
            ("Médico Demo",        "medico@sus.gov.br",   "medico123",   Usuario.PERFIL_MEDICO),
        ]:
            u = Usuario(nome=nome, email=email, perfil=perfil)
            u.set_senha(senha)
            db.session.add(u)
        db.session.commit()
        print("✅ Usuários padrão criados")