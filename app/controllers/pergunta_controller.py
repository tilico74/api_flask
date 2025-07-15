from flask import Blueprint, request, jsonify, render_template
from app.chatbot_class import JovemProgramadorChatbot  # ajuste caminho se necessário

pergunta_bp = Blueprint("pergunta", __name__, url_prefix="/pergunta")

# Instância global (carrega tudo uma vez só ao iniciar)
chatbot = JovemProgramadorChatbot()

@pergunta_bp.route('/', methods=['POST'])
def perguntar():
    data = request.get_json()

    if not data or 'pergunta' not in data:
        return jsonify({"erro": "Campo 'pergunta' é obrigatório"}), 400

    pergunta = data['pergunta']
    resposta = chatbot.chat(pergunta)

    return jsonify({"resposta": resposta}), 200

