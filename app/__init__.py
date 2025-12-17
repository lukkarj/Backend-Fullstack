from flask_openapi3 import OpenAPI, Info
from flask_cors import CORS

# Função que inicializa o aplicativo
def create_app():

    info = Info(title="Private CA Manager", version="1.0.0")
    app = OpenAPI(__name__, info=info)

    from .database import db

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///CAManager.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    CORS(app)


    with app.app_context():
        from app.controllers import api
        # Registra as rotas
        api.routes(app)
        # Cria schema do banco de dados
        db.create_all()

    return app