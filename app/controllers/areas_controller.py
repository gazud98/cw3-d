from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.area_model import Area
from app.extensions import db
from werkzeug.security import generate_password_hash
from flask import jsonify
areas_bp = Blueprint('areas', __name__, url_prefix='/areas')

@areas_bp.route('/')
def index():
    if "usuario" not in session:
        return redirect(url_for("auth.login"))

    areas = Area.query.order_by(Area.nombre).all()
    return render_template('areas/index.html', areas=areas, mostrar_navbar=True)


@areas_bp.route('/registrar', methods=['POST'])
def registrar_area():
    nombre = request.form['nombre'].strip()
    if not nombre:
        return jsonify({'success': False, 'errors': ['El nombre es obligatorio.']})
    
    if Area.query.filter_by(nombre=nombre).first():
        return jsonify({'success': False, 'errors': ['El nombre ya está registrado.']})
    
    nueva_area = Area(nombre=nombre)
    db.session.add(nueva_area)
    db.session.commit()
    return jsonify({'success': True})

@areas_bp.route('/editar/<int:id>', methods=['GET'])
def obtener_area(id):
    area = Area.query.get_or_404(id)
    return jsonify({
        'id': area.id,
        'nombre': area.nombre,
        'estado': area.estado
    })

@areas_bp.route('/actualizar/<int:id>', methods=['POST'])
def actualizar_area(id):
    area = Area.query.get_or_404(id)
    nombre = request.form['nombre'].strip()

    if not nombre:
        return jsonify({'success': False, 'errors': ['El nombre es obligatorio.']})

    if Area.query.filter(Area.nombre == nombre, Area.id != id).first():
        return jsonify({'success': False, 'errors': ['Ese nombre ya está en uso.']})

    area.nombre = nombre
    db.session.commit()
    return jsonify({'success': True})

@areas_bp.route('/toggle_estado/<int:id>', methods=['POST'])
def toggle_estado(id):
    area = Area.query.get_or_404(id)
    area.estado = not area.estado
    db.session.commit()
    return redirect(url_for("areas.index"))

@areas_bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_area(id):
    area = Area.query.get_or_404(id)
    db.session.delete(area)
    db.session.commit()
    return jsonify({'success': True})



@areas_bp.route('/lista')
def lista_parcial():
    area = Area.query.order_by(Area.nombre).all()
    return render_template("areas/lista.html", areas=area)