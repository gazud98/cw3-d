from app.extensions import db
from app.models.area_model import Area 


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), nullable=False)
    celular = db.Column(db.String(20))
    creado_en = db.Column(db.DateTime, server_default=db.func.now())
    activo = db.Column(db.Boolean, default=True)

    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'))
    area = db.relationship('Area', back_populates='usuarios')
   
    es_admin = db.Column(db.Boolean, default=False) 
