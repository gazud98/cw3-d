from app.extensions import db

class Carpeta(db.Model):
    __tablename__ = 'carpetas'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('carpetas.id'), nullable=True)  # Subcarpetas
    estado = db.Column(db.Boolean, default=True)

    subcarpetas = db.relationship('Carpeta', backref=db.backref('padre', remote_side=[id]))
    documentos = db.relationship('Documento', backref='carpeta', lazy=True)
