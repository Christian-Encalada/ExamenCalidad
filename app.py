from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
import os

app = Flask(__name__)
app.secret_key = '123456'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost:5432/gestion_viajes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contraseña = db.Column(db.String(120), nullable=False)

class Itinerario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario = db.relationship('Usuario', backref=db.backref('itinerarios', lazy=True))

class Vuelo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destino = db.Column(db.String(100))
    fecha_salida = db.Column(db.Date)
    precio = db.Column(db.Float)

class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50))  # Vuelo, Hotel
    detalles = db.Column(db.Text)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    usuario = db.relationship('Usuario', backref=db.backref('reservas', lazy=True))

class Notificacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mensaje = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.now)
    leida = db.Column(db.Boolean, default=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    usuario = db.relationship('Usuario', backref=db.backref('notificaciones', lazy=True))

class Reporte(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario = db.relationship('Usuario', backref=db.backref('reportes', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.before_request
def before_request():
    if current_user.is_authenticated:
        g.notificaciones_no_leidas = Notificacion.query.filter_by(id_usuario=current_user.id, leida=False).count()
    else:
        g.notificaciones_no_leidas = 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
@login_required
def home():
    vuelos = Vuelo.query.all()
    return render_template('home.html', vuelos=vuelos)

@app.route('/dashboard')
@login_required
def dashboard():
    itinerarios = Itinerario.query.filter_by(usuario_id=current_user.id).all()
    reservas = Reserva.query.filter_by(id_usuario=current_user.id).all()
    return render_template('dashboard.html', itinerarios=itinerarios, reservas=reservas)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        email = request.form['email']
        contraseña = request.form['contraseña']
        nuevo_usuario = Usuario(nombre_usuario=nombre_usuario, email=email, contraseña=contraseña)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('¡Registro exitoso! Por favor inicia sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        contraseña = request.form['contraseña']
        usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
        if usuario and usuario.contraseña == contraseña:
            login_user(usuario)
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Credenciales incorrectas. Por favor intenta de nuevo.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('¡Has cerrado sesión exitosamente!', 'success')
    return redirect(url_for('index'))

@app.route('/notificaciones')
@login_required
def notificaciones():
    notificaciones = Notificacion.query.filter_by(id_usuario=current_user.id).order_by(Notificacion.fecha.desc()).all()
    return render_template('notificaciones.html', notificaciones=notificaciones)

@app.route('/notificaciones/<int:id>/leer', methods=['POST'])
@login_required
def leer_notificacion(id):
    notificacion = Notificacion.query.get_or_404(id)
    notificacion.leida = True
    db.session.commit()
    return redirect(url_for('notificaciones'))

@app.route('/itinerarios', methods=['GET', 'POST'])
@login_required
def gestionar_itinerarios():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
        nuevo_itinerario = Itinerario(titulo=titulo, descripcion=descripcion, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, usuario_id=current_user.id)
        db.session.add(nuevo_itinerario)
        db.session.commit()
        flash('¡Itinerario creado exitosamente!', 'success')
        return redirect(url_for('gestionar_itinerarios'))
    itinerarios = Itinerario.query.filter_by(usuario_id=current_user.id).all()
    return render_template('itinerarios.html', itinerarios=itinerarios)

@app.route('/itinerario/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_itinerario():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
        nuevo_itinerario = Itinerario(titulo=titulo, descripcion=descripcion, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, usuario_id=current_user.id)
        db.session.add(nuevo_itinerario)
        db.session.commit()
        flash('¡Itinerario creado exitosamente!', 'success')
        return redirect(url_for('gestionar_itinerarios'))
    return render_template('nuevo_itinerario.html')

@app.route('/itinerario/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_itinerario(id):
    itinerario = Itinerario.query.get_or_404(id)
    if request.method == 'POST':
        itinerario.titulo = request.form['titulo']
        itinerario.descripcion = request.form['descripcion']
        itinerario.fecha_inicio = datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d')
        itinerario.fecha_fin = datetime.strptime(request.form['fecha_fin'], '%Y-%m-%d')
        db.session.commit()
        flash('¡Itinerario actualizado exitosamente!', 'success')
        return redirect(url_for('gestionar_itinerarios'))
    return render_template('editar_itinerario.html', itinerario=itinerario)

@app.route('/itinerario/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_itinerario(id):
    itinerario = Itinerario.query.get_or_404(id)
    db.session.delete(itinerario)
    db.session.commit()
    flash('¡Itinerario eliminado exitosamente!', 'success')
    return redirect(url_for('gestionar_itinerarios'))

@app.route('/reservar_vuelo/<int:vuelo_id>')
@login_required
def reservar_vuelo(vuelo_id):
    vuelo = Vuelo.query.get_or_404(vuelo_id)
    nueva_reserva = Reserva(tipo="Vuelo", detalles=f"Reserva para vuelo a {vuelo.destino} el {vuelo.fecha_salida}", id_usuario=current_user.id)
    db.session.add(nueva_reserva)
    db.session.commit()

    # Crear una notificación
    nueva_notificacion = Notificacion(mensaje=f"Reserva realizada para vuelo a {vuelo.destino} el {vuelo.fecha_salida}", leida=False, id_usuario=current_user.id)
    db.session.add(nueva_notificacion)
    db.session.commit()

    flash('¡Reserva realizada exitosamente!', 'success')
    return redirect(url_for('home'))

@app.route('/reportes')
@login_required
def listar_reportes():
    reportes = Reporte.query.filter_by(usuario_id=current_user.id).all()
    return render_template('reportes.html', reportes=reportes)

@app.route('/reporte/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_reporte():
    if request.method == 'POST':
        tipo = request.form['tipo']
        descripcion = request.form['descripcion']
        fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d')
        nuevo_reporte = Reporte(tipo=tipo, descripcion=descripcion, fecha=fecha, usuario_id=current_user.id)
        db.session.add(nuevo_reporte)
        db.session.commit()
        flash('Reporte creado exitosamente', 'success')
        return redirect(url_for('listar_reportes'))
    return render_template('nuevo_reporte.html')

@app.route('/reporte/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_reporte(id):
    reporte = Reporte.query.get_or_404(id)
    if request.method == 'POST':
        reporte.tipo = request.form['tipo']
        reporte.descripcion = request.form['descripcion']
        reporte.fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d')
        db.session.commit()
        flash('Reporte actualizado exitosamente', 'success')
        return redirect(url_for('listar_reportes'))
    return render_template('editar_reporte.html', reporte=reporte)

@app.route('/reporte/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_reporte(id):
    reporte = Reporte.query.get_or_404(id)
    db.session.delete(reporte)
    db.session.commit()
    flash('Reporte eliminado exitosamente', 'success')
    return redirect(url_for('listar_reportes'))

def init_db():
    if not Vuelo.query.first():
        vuelos = [
            Vuelo(destino="Nueva York", fecha_salida=datetime(2024, 9, 1), precio=500),
            Vuelo(destino="París", fecha_salida=datetime(2024, 10, 15), precio=600),
            Vuelo(destino="Tokio", fecha_salida=datetime(2024, 11, 20), precio=700),
            Vuelo(destino="Londres", fecha_salida=datetime(2024, 12, 5), precio=450),
            Vuelo(destino="Madrid", fecha_salida=datetime(2025, 1, 10), precio=550)
        ]
        db.session.add_all(vuelos)
        db.session.commit()

    if not Usuario.query.first():
        usuario = Usuario(nombre_usuario='admin', email='admin@example.com', contraseña='admin')
        db.session.add(usuario)
        db.session.commit()
        
    if Usuario.query.get(1):
        itinerarios = [
            Itinerario(titulo="Nueva York", descripcion="Visita a la Estatua de la Libertad y Times Square", fecha_inicio=datetime(2024, 9, 1), fecha_fin=datetime(2024, 9, 10), usuario_id=1),
            Itinerario(titulo="París", descripcion="Torre Eiffel y museo del Louvre", fecha_inicio=datetime(2024, 10, 15), fecha_fin=datetime(2024, 10, 20), usuario_id=1),
            Itinerario(titulo="Tokio", descripcion="Visita a templos y cultura japonesa", fecha_inicio=datetime(2024, 11, 20), fecha_fin=datetime(2024, 11, 30), usuario_id=1)
        ]
        notificaciones = [
            Notificacion(mensaje="Recuerda tu vuelo a Nueva York el 2024-09-01", leida=False, id_usuario=1),
            Notificacion(mensaje="Recuerda tu vuelo a París el 2024-10-15", leida=False, id_usuario=1),
            Notificacion(mensaje="Recuerda tu vuelo a Tokio el 2024-11-20", leida=False, id_usuario=1)
        ]
        db.session.add_all(itinerarios + notificaciones)
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
