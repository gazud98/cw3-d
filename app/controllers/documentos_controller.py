from flask import (
    Blueprint,
    request,
    jsonify,
    redirect,
    url_for,
    render_template,
    session,
)
from app.models.documento_model import Documento, DocumentoPapelera
from app.extensions import db
import os
from werkzeug.utils import secure_filename
import time
from datetime import datetime
from flask_mail import Message
from app.extensions import mail
from app.utils.graph_helper import enviar_correo_graph
from app.models.solicitud_model import SolicitudRevision
documentos_bp = Blueprint("documentos", __name__, url_prefix="/documentos")

UPLOAD_FOLDER = os.path.join("app","static", "uploads", "documentos")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Crear la carpeta si no existe


@documentos_bp.route("/subir", methods=["POST"])
def subir_documento():
    nombre = request.form.get("nombre")
    tipo = request.form.get("tipo")
    carpeta_id = request.form.get("carpeta_id")
    archivo = request.files.get("archivo")
    correo = request.form.get("correo")
    reemplazar = request.args.get("reemplazar", "0") == "1"

    if not nombre or not tipo or not archivo:
        return jsonify({"success": False, "error": "Faltan campos requeridos."})

    # Validar extensión
    extensiones_permitidas = (".pdf", ".xls", ".xlsx")
    filename = secure_filename(archivo.filename)
    if not filename.lower().endswith(extensiones_permitidas):
        return jsonify(
            {
                "success": False,
                "error": "Tipo de archivo no permitido. Solo PDF o Excel.",
            }
        )

    # Verificar si ya existe documento con mismo nombre, tipo y carpeta
    existente = Documento.query.filter_by(
        nombre=nombre, tipo=tipo, carpeta_id=carpeta_id,correo_destino=correo
    ).first()

    if existente and not reemplazar:
        return jsonify(
            {
                "success": False,
                "existe": True,
                "id": existente.id,
                "mensaje": f"Ya existe un documento llamado '{nombre}' en esta carpeta.",
            }
        )

    ruta = os.path.join(UPLOAD_FOLDER, filename)
    archivo.save(ruta)
    ruta_relativa = os.path.join("static", "uploads", "documentos", filename).replace("\\", "/")


    if existente and reemplazar:
        try:
            if existente.ruta_archivo and os.path.exists(existente.ruta_archivo):
                os.remove(existente.ruta_archivo)
            # Aquí más adelante moveremos a papelera
        except Exception:
            pass

        existente.ruta_archivo = ruta_relativa
        existente.correo_destino = correo
        db.session.commit()
        return jsonify({"success": True, "reemplazado": True})

    nuevo_doc = Documento(
        nombre=nombre, tipo=tipo, ruta_archivo=ruta_relativa, carpeta_id=carpeta_id,correo_destino=correo
    )
    db.session.add(nuevo_doc)
    db.session.commit()

    return jsonify({"success": True})


@documentos_bp.route("/eliminar/<int:id>", methods=["POST"])
def eliminar_documento(id):
    documento = Documento.query.get_or_404(id)
    mover_a_papelera(documento)
    return jsonify({"success": True})


@documentos_bp.route("/obtener/<int:id>")
def obtener_documento(id):
    documento = Documento.query.get_or_404(id)
    return jsonify(
        {
            "id": documento.id,
            "nombre": documento.nombre,
            "tipo": documento.tipo,
            "ruta_archivo": documento.ruta_archivo,
            "carpeta_id": documento.carpeta_id,
        }
    )


@documentos_bp.route("/listar_documentos/<int:carpeta_id>")
def listar_documentos(carpeta_id):
    documentos = (
        Documento.query.filter_by(carpeta_id=carpeta_id)
        .order_by(Documento.nombre)
        .all()
    )
    resultado = []

    for doc in documentos:
        resultado.append(
            {
                "id": doc.id,
                "nombre": doc.nombre,
                "tipo": doc.tipo,
                "ruta_archivo": doc.ruta_archivo,
            }
        )

    return jsonify(resultado)


@documentos_bp.route("/actualizar/<int:id>", methods=["POST"])
def actualizar_documento(id):
    documento = Documento.query.get_or_404(id)
    nuevo_nombre = request.form.get("nombre")
    nuevo_archivo = request.files.get("archivo")

    if not nuevo_nombre:
        return jsonify({"success": False, "error": "El nombre es obligatorio."})

    documento.nombre = nuevo_nombre

    if nuevo_archivo:
        # Validar tipo de archivo
        extensiones_permitidas = (".pdf", ".xls", ".xlsx")
        filename = secure_filename(nuevo_archivo.filename)

        if not filename.lower().endswith(extensiones_permitidas):
            return jsonify(
                {
                    "success": False,
                    "error": "Tipo de archivo no permitido. Solo PDF o Excel.",
                }
            )

        # Eliminar archivo anterior si existe
        try:
            if documento.ruta_archivo and os.path.exists(documento.ruta_archivo):
                os.remove(documento.ruta_archivo)
        except Exception:
            pass

        # Guardar nuevo archivo
        ruta = os.path.join(UPLOAD_FOLDER, filename)
        nuevo_archivo.save(ruta)
        ruta_relativa = os.path.join("uploads", "documentos", filename).replace("\\", "/")


        documento.ruta_archivo = ruta_relativa
        documento.tipo = "excel" if filename.endswith((".xls", ".xlsx")) else "pdf"

    db.session.commit()

    return jsonify({"success": True})


def mover_a_papelera(documento):
    papelera = DocumentoPapelera(
        nombre=documento.nombre,
        tipo=documento.tipo,
        ruta_archivo=documento.ruta_archivo,
        carpeta_id=documento.carpeta_id,
    )
    db.session.add(papelera)
    db.session.delete(documento)
    db.session.commit()


@documentos_bp.route('/papelera')
def vista_papelera():
    if "usuario" not in session:
        return redirect(url_for("auth.login"))


    documentos = DocumentoPapelera.query.order_by(DocumentoPapelera.fecha_eliminado.desc()).all()
    return render_template("carpetas/papelera.html", documentos=documentos)


@documentos_bp.route('/recuperar/<int:id>', methods=["POST"])
def recuperar_documento(id):
    doc = DocumentoPapelera.query.get_or_404(id)

    nuevo = Documento(
        nombre=doc.nombre,
        tipo=doc.tipo,
        ruta_archivo=doc.ruta_archivo,
        carpeta_id=doc.carpeta_id
    )
    db.session.add(nuevo)
    db.session.delete(doc)
    db.session.commit()

    return jsonify({"success": True})




@documentos_bp.route('/subir_copia_revision/<int:documento_id>', methods=["POST"])
def subir_copia_revision(documento_id):
    archivo = request.files.get("archivo")
    user_id = session.get("usuario_id")

    if not archivo or not documento_id or not user_id:
        return jsonify({"success": False, "error": "Datos incompletos."})

    documento = Documento.query.get_or_404(documento_id)

    # Generar nombre único con fecha y hora
    original_filename = secure_filename(archivo.filename)
    nombre_base, extension = os.path.splitext(original_filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"{nombre_base}_{timestamp}{extension}"

    # Guardar archivo en ruta segura
    carpeta_destino = os.path.join("app", "static", "uploads", "copias_revision")
    ruta_completa = os.path.join(carpeta_destino, nombre_archivo)
    os.makedirs(carpeta_destino, exist_ok=True)
    archivo.save(ruta_completa)

    # Ruta relativa para servir en navegador
    ruta_relativa = os.path.join("uploads", "copias_revision", nombre_archivo).replace("\\", "/")

    # Crear registro de revisión
    nueva = SolicitudRevision(
        documento_id=documento_id,
        nombre_archivo=nombre_archivo,
        ruta_archivo=ruta_relativa,
        creado_por=user_id
    )
    db.session.add(nueva)
    db.session.commit()

    # Enviar notificación por correo al líder
    if documento.correo_destino:
        try:
            url_dashboard = request.host_url.rstrip('/') + url_for('solicitudes.vista_solicitudes_revision')
            asunto = f"Nueva solicitud de revisión - {documento.nombre}"
            cuerpo = (
                f"Se ha subido una nueva copia del documento para su revisión: {documento.nombre}\n\n"
                f"Revisar solicitud aquí: {url_dashboard}"
            )
            enviar_correo_graph(documento.correo_destino, asunto, cuerpo)
        except Exception as e:
            print("Error enviando correo:", e)

    return jsonify({"success": True})
