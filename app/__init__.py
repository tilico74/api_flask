from flask import Flask
from app.controllers.pergunta_controller import pergunta_bp
from app.controllers.views import views_bp

def create_app():
    app = Flask(__name__)

    
    app.register_blueprint(pergunta_bp)
    app.register_blueprint(views_bp)
    return app