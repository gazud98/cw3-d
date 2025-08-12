from app import create_app
from app.extensions import db
from app.models.user_model import User, Area
from werkzeug.security import generate_password_hash

# Creamos la app con el contexto de Flask
app = create_app()

with app.app_context():
    # 1. Buscar o crear el área 'GESTIÓN SISTEMAS'
    area = Area.query.filter_by(nombre='GESTIÓN SISTEMAS').first()
    if not area:
        area = Area(nombre='GESTIÓN SISTEMAS')
        db.session.add(area)
        db.session.commit()
        print("✅ Área 'GESTIÓN SISTEMAS' creada.")

    # 2. Verificar si ya existe el usuario admin
    existing_admin = User.query.filter_by(username='admin').first()
    if existing_admin:
        db.session.delete(existing_admin)
        db.session.commit()
        print("🗑 Usuario 'admin' anterior eliminado.")

    # 3. Crear nuevo usuario admin con contraseña encriptada
    admin = User(
        username='admin',
        password=generate_password_hash('admin123'),
        nombre_completo='Administrador General',
        correo='admin@sgc.com',
        celular='3100000000',
        area_id=area.id,
        es_admin=True
    )
    db.session.add(admin)
    db.session.commit()
    print("✅ Usuario administrador creado con éxito: admin / admin123")
