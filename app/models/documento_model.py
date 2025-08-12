from app.extensions import db

class Documento(db.Model):
    __tablename__ = 'documentos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # Puede ser "excel" o "pdf"
    ruta_archivo = db.Column(db.String(300), nullable=False)  # Ruta donde se almacena el archivo
    carpeta_id = db.Column(db.Integer, db.ForeignKey('carpetas.id'), nullable=False)
    correo_destino = db.Column(db.String(255), nullable=True) 
    estado = db.Column(db.Boolean, default=True)  # Por si quieren "ocultar" archivos


class DocumentoPapelera(db.Model):
    __tablename__ = 'documentos_papelera'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    ruta_archivo = db.Column(db.Text, nullable=False)
    carpeta_id = db.Column(db.Integer)
    fecha_eliminado = db.Column(db.DateTime, server_default=db.func.now())