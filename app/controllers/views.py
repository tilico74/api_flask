from flask import Blueprint, render_template

views_bp = Blueprint("views", __name__)

@views_bp.route("/home")
def home():
    return render_template("home.html", banner_home= True)

@views_bp.route("/funcionalidades")
def funcionalidades():
    return render_template("funcionalidades.html")

@views_bp.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@views_bp.route("/desenvolvedor")
def desenvolvedor():
    return render_template("desenvolvedor.html")

@views_bp.route("/requisitos")
def requisitos():
    return render_template("requisitos.html")


