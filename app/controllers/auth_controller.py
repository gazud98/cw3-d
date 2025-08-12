from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.user_model import User, Area
from app.extensions import db
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from app.models.solicitud_model import SolicitudRevision
from app.models.documento_model import Documento
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip().lower()
        password = request.form["password"].strip().lower()

        user = User.query.filter_by(username=username).first()

        if not user:
            flash("El usuario no existe.")
        elif not user.password:
            flash("El usuario no tiene contraseña configurada.")
        elif not check_password_hash(user.password, password):
            flash("Contraseña incorrecta.")
        else:
            session["usuario"] = user.username
            session["usuario_id"] = user.id
            session["nombre_completo"] = user.nombre_completo
            session["area_id"] = user.area_id
            session["es_admin"] = user.es_admin
            return redirect(url_for("auth.dashboard"))

    return render_template("login.html")



@auth_bp.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("auth.login"))
    usuario_id = session["usuario_id"]
    nuevas_solicitudes = SolicitudRevision.query.filter_by(estado=1).count()
    nuevas_respuestas = SolicitudRevision.query.filter(
        SolicitudRevision.creado_por == usuario_id,
        SolicitudRevision.estado.in_([2, 3]),
        SolicitudRevision.fecha_revisado != None
    ).order_by(SolicitudRevision.fecha_revisado.desc()).limit(5).all()

    return render_template(
        "dashboard.html",
        mostrar_navbar=True,
        nuevas_solicitudes=nuevas_solicitudes,
        solicitudes_pendientes=nuevas_solicitudes,
        usuario=session["usuario"],
        nuevas_respuestas=nuevas_respuestas
    )

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


