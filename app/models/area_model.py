from app.extensions import db

class Area(db.Model):
    __tablename__ = 'areas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    estado = db.Column(db.Boolean, default=True)
    usuarios = db.relationship('User', back_populates='area')