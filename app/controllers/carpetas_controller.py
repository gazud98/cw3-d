from flask import (
    Blueprint,
    request,
    jsonify,
    redirect,
    url_for,
    render_template,
    session,
)
from app.models.carpeta_model import Carpeta
from app.models.documento_model import Documento
from app.extensions import db

carpetas_bp = Blueprint("carpetas", __name__, url_prefix="/carpetas")


@carpetas_bp.route("/")
def index():
    if "usuario" not in session:
        return redirect(url_for("auth.login"))

    carpetas = Carpeta.query.filter_by(parent_id=None).order_by(Carpeta.nombre).all()
    return render_template("carpetas/index.html", carpetas=carpetas)


@carpetas_bp.route("/crear", methods=["POST"])
def crear_carpeta():
    if not session.get("es_admin"):
      return jsonify({"success": False, "error": "No autorizado"}), 403

    data = request.get_json()
    nombre = data.get("nombre")
    parent_id = data.get("parent_id") or None

    if not nombre:
        return jsonify({"success": False, "error": "Nombre requerido"})

    
    if Carpeta.query.filter_by(nombre=nombre, parent_id=parent_id).first():
        return jsonify(
            {
                "success": False,
                "error": "Ya existe una carpeta con ese nombre en esta ubicación.",
            }
        )

    nueva_carpeta = Carpeta(nombre=nombre, parent_id=parent_id)
    db.session.add(nueva_carpeta)
    db.session.commit()

    return jsonify({"success": True})


@carpetas_bp.route("/actualizar/<int:id>", methods=["POST"])
def actualizar_carpeta(id):
    if not session.get("es_admin"):
      return jsonify({"success": False, "error": "No autorizado"}), 403
    carpeta = Carpeta.query.get_or_404(id)

    nombre = request.form.get("nombre")

    if not nombre:
        return jsonify({"success": False, "error": "Nombre requerido"})

    if Carpeta.query.filter(Carpeta.id != id, Carpeta.nombre == nombre).first():
        return jsonify(
            {"success": False, "error": "Ya existe otra carpeta con ese nombre"}
        )

    carpeta.nombre = nombre
    db.session.commit()

    return jsonify({"success": True})


@carpetas_bp.route("/eliminar/<int:id>", methods=["POST"])
def eliminar_carpeta(id):
    if not session.get("es_admin"):
      return jsonify({"success": False, "error": "No autorizado"}), 403
    carpeta = Carpeta.query.get_or_404(id)

    if carpeta.subcarpetas or carpeta.documentos:
        return jsonify(
            {
                "success": False,
                "error": "No puedes eliminar una carpeta que tiene contenido.",
            }
        )

    db.session.delete(carpeta)
    db.session.commit()

    return jsonify({"success": True})


@carpetas_bp.route("/obtener/<int:id>")
def obtener_carpeta(id):
    carpeta = Carpeta.query.get_or_404(id)
    return jsonify(
        {"id": carpeta.id, "nombre": carpeta.nombre, "parent_id": carpeta.parent_id}
    )


@carpetas_bp.route("/listar_carpetas")
def listar_carpetas():
    carpetas = Carpeta.query.filter_by(parent_id=None).order_by(Carpeta.nombre).all()
    resultado = []

    for carpeta in carpetas:
        resultado.append({"id": carpeta.id, "nombre": carpeta.nombre})

    return jsonify(resultado)


@carpetas_bp.route("/contenido/<int:parent_id>", methods=["GET"])
@carpetas_bp.route("/contenido/", defaults={"parent_id": None}, methods=["GET"])
def obtener_contenido(parent_id):
    carpetas = (
        Carpeta.query.filter_by(parent_id=parent_id).order_by(Carpeta.nombre).all()
    )
    documentos = (
        Documento.query.filter_by(carpeta_id=parent_id).order_by(Documento.nombre).all()
    )

    return jsonify(
        {
            "carpetas": [{"id": c.id, "nombre": c.nombre} for c in carpetas],
            "documentos": [
                {
                    "id": d.id,
                    "nombre": d.nombre,
                    "tipo": d.tipo,
                    "ruta_archivo": d.ruta_archivo,
                }
                for d in documentos
            ],
        }
    )
