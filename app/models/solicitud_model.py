from app.extensions import db
from datetime import datetime
from app.models.user_model import User
from app.models.documento_model import Documento

class SolicitudRevision(db.Model):
    __tablename__ = 'solicitudes_revision'

    id = db.Column(db.Integer, primary_key=True)
    documento_id = db.Column(db.Integer, db.ForeignKey("documentos.id"))
    nombre_archivo = db.Column(db.String(255))
    ruta_archivo = db.Column(db.String(255))
    creado_por = db.Column(db.Integer, db.ForeignKey("users.id"))
    fecha_envio = db.Column(db.DateTime, default=db.func.now())
    
    estado = db.Column(db.Integer, default=1)  # 1: Pendiente, 2: Aprobado, 3: Rechazado
    comentario = db.Column(db.Text)
    revisado_por = db.Column(db.Integer, db.ForeignKey("users.id"))
    fecha_revisado = db.Column(db.DateTime)

    documento = db.relationship("Documento", backref="solicitudes")
    creador = db.relationship("User", foreign_keys=[creado_por])
    revisor = db.relationship("User", foreign_keys=[revisado_por])
