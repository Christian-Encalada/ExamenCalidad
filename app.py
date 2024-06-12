from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = '123456'

# Configuración de PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ubam6xu3ymklpokeg7hq:1t7pZ38diFrObgbAU7iJFcdojR9ivq@bpby7a2d2t1yw4necchg-postgresql.services.clever-cloud.com:50013/bpby7a2d2t1yw4necchg'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Definición de modelos
class Usuarios(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(100))
    email = db.Column(db.String(100))
    contraseña = db.Column(db.String(100))

class Temas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    fecha_creacion = db.Column(db.Date)
    usuario = db.relationship('Usuarios', backref=db.backref('temas', lazy=True))

class Respuestas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_tema = db.Column(db.Integer, db.ForeignKey('temas.id'))
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    contenido = db.Column(db.Text)
    fecha_respuesta = db.Column(db.Date)
    tema = db.relationship('Temas', backref=db.backref('respuestas', lazy=True))
    usuario = db.relationship('Usuarios', backref=db.backref('respuestas', lazy=True))

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Función para cargar el usuario desde la base de datos
@login_manager.user_loader
def load_user(user_id):
    return Usuarios.query.get(int(user_id))

# Rutas y vistas para registro e inicio de sesión
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if Usuarios.query.filter_by(nombre_usuario=username).first():
            flash('El nombre de usuario ya está en uso', 'error')
            return redirect(url_for('registro'))

        nuevo_usuario = Usuarios(nombre_usuario=username, email=email, contraseña=password)
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash('¡Registro exitoso! Por favor inicia sesión.', 'success')
        return redirect(url_for('login'))

    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        usuario = Usuarios.query.filter_by(nombre_usuario=username).first()
        if usuario and usuario.contraseña == password:
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
@login_required
def home():
    temas = Temas.query.all()
    return render_template('home.html', temas=temas)

@app.route('/agregar_tema', methods=['GET', 'POST'])
@login_required
def agregar_tema():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        id_usuario = current_user.id

        nuevo_tema = Temas(
            titulo=titulo,
            descripcion=descripcion,
            id_usuario=id_usuario,
            fecha_creacion=datetime.now()
        )

        db.session.add(nuevo_tema)
        db.session.commit()

        return redirect(url_for('ver_tema', id_tema=nuevo_tema.id))
    
    return render_template('agregar_tema.html')

@app.route('/temas/<int:id_tema>')
@login_required
def ver_tema(id_tema):
    tema = Temas.query.get_or_404(id_tema)
    respuestas = Respuestas.query.filter_by(id_tema=id_tema).all()
    return render_template('ver_tema.html', tema=tema, respuestas=respuestas)

@app.route('/temas/<int:id_tema>/agregar_respuesta', methods=['POST'])
@login_required
def agregar_respuesta(id_tema):
    contenido = request.form['contenido']
    id_usuario = current_user.id

    nueva_respuesta = Respuestas(
        id_tema=id_tema,
        id_usuario=id_usuario,
        contenido=contenido,
        fecha_respuesta=datetime.now()
    )

    db.session.add(nueva_respuesta)
    db.session.commit()

    flash('Respuesta agregada satisfactoriamente', 'success')
    return redirect(url_for('ver_tema', id_tema=id_tema))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=False)

