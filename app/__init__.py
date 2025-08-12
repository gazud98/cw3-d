from flask import Flask
from app.config import Config
from app.extensions import db  
from app.controllers.auth_controller import auth_bp
from app.controllers.carpetas_controller import carpetas_bp
from app.controllers.documentos_controller import documentos_bp
from app.controllers.usuarios_controller import usuarios_bp
from app.controllers.areas_controller import areas_bp
from app.controllers.solicitudes_controller import solicitudes_bp
from app.extensions import mail

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    mail.init_app(app)
    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(carpetas_bp)
    app.register_blueprint(documentos_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(areas_bp)
    app.register_blueprint(solicitudes_bp)
    return app
