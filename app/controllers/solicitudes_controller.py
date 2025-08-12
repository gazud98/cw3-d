from flask import (
    Blueprint,
    request,
    jsonify,
    redirect,
    url_for,
    render_template,
    session,
)
from app.models.solicitud_model import SolicitudRevision
from app.extensions import db
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from app.utils.graph_helper import enviar_correo_graph


solicitudes_bp = Blueprint("solicitudes", __name__, url_prefix="/solicitudes")


@solicitudes_bp.route("/solicitudes_revision")
def vista_solicitudes_revision():
    if "usuario" not in session:
        return redirect(url_for("auth.login"))

    solicitudes = SolicitudRevision.query.order_by(
        SolicitudRevision.estado.asc(), SolicitudRevision.fecha_envio.desc()
    ).all()

    return render_template(
        "solicitudes/index.html", solicitudes=solicitudes, mostrar_navbar=True
    )


@solicitudes_bp.route("/marcar_revisado/<int:id>", methods=["POST"])
def marcar_revisado(id):
    solicitud = SolicitudRevision.query.get_or_404(id)
    solicitud.revisado = True
    solicitud.revisado_por = session.get("usuario_id")
    solicitud.fecha_revisado = datetime.now()  # ← Guardar la fecha y hora actual
    db.session.commit()
    return jsonify({"success": True})


@solicitudes_bp.route("/rechazar/<int:id>", methods=["POST"])
def rechazar_solicitud(id):
    data = request.get_json()
    comentario = data.get("comentario", "").strip()
    user_id = session.get("usuario_id")

    if not comentario:
        return jsonify(
            {"success": False, "error": "Comentario requerido para rechazar."}
        )

    solicitud = SolicitudRevision.query.get_or_404(id)
    solicitud.estado = 3  # Rechazado
    solicitud.comentario = comentario
    solicitud.revisado_por = user_id
    solicitud.fecha_revisado = datetime.now()

    db.session.commit()
    # Notificar al creador si tiene correo
    if solicitud.creador and solicitud.creador.correo:
     try:
        asunto = "Tu solicitud ha sido rechazada"
        cuerpo = (
            f"Hola {solicitud.creador.nombre_completo},\n\n"
            f"Tu solicitud para el documento '{solicitud.documento.nombre}' fue *rechazada*.\n\n"
            f"Motivo del rechazo:\n{comentario}"
        )
        enviar_correo_graph(solicitud.creador.correo, asunto, cuerpo)
     except Exception as e:
        print("Error enviando correo de rechazo:", e)

    return jsonify({"success": True})


@solicitudes_bp.route("/aprobar/<int:id>", methods=["POST"])
def aprobar_solicitud(id):
    solicitud = SolicitudRevision.query.get_or_404(id)
    archivo_firmado = request.files.get("archivo_firmado")
    user_id = session.get("usuario_id")

    if not archivo_firmado:
        return jsonify({"success": False, "error": "Archivo firmado requerido"})

    # Eliminar archivo anterior si existe
    try:
        path_actual = os.path.join("app/static", solicitud.ruta_archivo)
        if os.path.exists(path_actual):
            os.remove(path_actual)
    except Exception:
        pass

    # Guardar el nuevo archivo firmado sobrescribiendo
    nombre_firmado = f"firmado_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secure_filename(archivo_firmado.filename)}"
    ruta_relativa = os.path.join("uploads/copias_revision", nombre_firmado)
    ruta_completa = os.path.join("app/static", ruta_relativa)
    os.makedirs(os.path.dirname(ruta_completa), exist_ok=True)
    archivo_firmado.save(ruta_completa)

    # Actualizar campos de revisión
    solicitud.ruta_archivo = ruta_relativa
    solicitud.estado = 2  # Aprobado
    solicitud.fecha_revisado = datetime.now()
    solicitud.revisado_por = user_id

    db.session.commit()

    # Notificar al creador si tiene correo


    if solicitud.creador and solicitud.creador.correo:
     try:
        asunto = "Tu solicitud ha sido aprobada"
        cuerpo = (
            f"Hola {solicitud.creador.nombre_completo},\n\n"
            f"Tu solicitud para el documento '{solicitud.documento.nombre}' fue *aprobada*.\n"
            f"Puedes consultar la versión firmada desde el sistema."
        )
        enviar_correo_graph(solicitud.creador.correo, asunto, cuerpo)
     except Exception as e:
        print("Error enviando correo de aprobación:", e)

    return jsonify({"success": True})
