import os

from flask import Flask

from backend import db
from backend.models import init_db
from backend.routes import api_bp


def create_app(test_config=None):
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
    app = Flask(__name__, static_folder=frontend_dir, static_url_path='/static')
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///{}'.format(os.path.join(os.path.dirname(__file__), 'database.db')),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is not None:
        app.config.update(test_config)

    # Inicializa o módulo de banco de dados e registra rotas.
    db.init_app(app)
    app.register_blueprint(api_bp)

    # Cria o banco de dados e popula com dados de exemplo se necessário.
    with app.app_context():
        init_db(app)

    @app.route('/')
    def home():
        return app.send_static_file('index.html')

    @app.route('/admin')
    def admin():
        return app.send_static_file('admin.html')

    return app


if __name__ == '__main__':
    application = create_app()
    application.run(host='0.0.0.0', port=5000, debug=True)
