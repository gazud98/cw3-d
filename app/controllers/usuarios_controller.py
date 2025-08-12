from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.user_model import User, Area
from app.models.area_model import Area
from app.extensions import db
from werkzeug.security import generate_password_hash
from flask import jsonify

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


@usuarios_bp.route("/")
def index():
    if "usuario" not in session:
        return redirect(url_for("auth.login"))

    usuarios = User.query.order_by(User.nombre_completo).all()
    areas = Area.query.order_by(Area.nombre).all()
    return render_template(
        "usuarios/index.html", usuarios=usuarios, areas=areas, mostrar_navbar=True
    )


@usuarios_bp.route("/eliminar/<int:id>", methods=["POST"])
def eliminar_usuario(id):
    if "usuario" not in session:
        return redirect(url_for("auth.login"))

    usuario = User.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    flash("Usuario eliminado correctamente.")
    return redirect(url_for("usuarios.index"))


@usuarios_bp.route("/editar/<int:id>", methods=["GET"])
def obtener_usuario(id):
    usuario = User.query.get_or_404(id)
    return {
        "id": usuario.id,
        "username": usuario.username,
        "nombre_completo": usuario.nombre_completo,
        "correo": usuario.correo,
        "celular": usuario.celular or "",
        "area_id": usuario.area_id,
        "es_admin": usuario.es_admin,
    }


@usuarios_bp.route("/actualizar/<int:id>", methods=["POST"])
def actualizar_usuario(id):
   
    usuario = User.query.get_or_404(id)



    # Asignar los nuevos valores
    usuario.username = request.form["username"]
    usuario.nombre_completo = request.form["nombre_completo"]
    usuario.correo = request.form["correo"]
    usuario.celular = request.form["celular"]
    usuario.area_id = request.form["area_id"]
    usuario.es_admin = "es_admin" in request.form

    password = request.form.get("password")
    if password:
        usuario.password = generate_password_hash(password)

    db.session.commit()
    return jsonify({"success": True})




@usuarios_bp.route("/registrar", methods=["POST"])
def registrar_usuario():
    if "usuario" not in session:
        return jsonify({"success": False, "errors": ["Sesión no válida."]})

    username = request.form["username"]
    password = request.form["password"]
    confirm = request.form["confirm"]
    nombre = request.form["nombre_completo"]
    correo = request.form["correo"]
    celular = request.form["celular"]
    area_id = request.form["area_id"]
    es_admin = "es_admin" in request.form

    errores = []

    if not username or not password or not confirm or not nombre or not correo:
        errores.append("Todos los campos marcados son obligatorios.")
    elif password != confirm:
        errores.append("Las contraseñas no coinciden.")
    elif User.query.filter_by(username=username).first():
        errores.append("El nombre de usuario ya existe.")

    if errores:
        return jsonify({"success": False, "errors": errores})

    nuevo_usuario = User(
        username=username,
        password=generate_password_hash(password),
        nombre_completo=nombre,
        correo=correo,
        celular=celular,
        area_id=area_id,
        es_admin=es_admin,
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({"success": True})


@usuarios_bp.route("/lista")
def lista_parcial():
    usuarios = User.query.order_by(User.nombre_completo).all()
    return render_template("usuarios/lista.html", usuarios=usuarios)


@usuarios_bp.route("/toggle_estado/<int:id>", methods=["POST"])
def toggle_estado(id):
    usuario = User.query.get_or_404(id)

    # No permitir desactivar al super admin
    if usuario.es_admin:
        flash("No se puede cambiar el estado de un administrador.")
        return redirect(url_for("usuarios.index"))

    usuario.activo = not usuario.activo
    db.session.commit()
    return redirect(url_for("usuarios.index"))
