from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = '123456'

# Configuración de PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost:5432/foro_linea'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Definición de modelos
class Usuarios(db.Model):
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

# Rutas
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para agregar un usuario
@app.route('/agregar_usuario', methods=['GET', 'POST'])
def agregar_usuario():
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        email = request.form['email']
        contraseña = request.form['contraseña']
        
        # Creamos un nuevo usuario y lo agregamos a la base de datos
        nuevo_usuario = Usuarios(nombre_usuario=nombre_usuario, email=email, contraseña=contraseña)
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        flash('Usuario agregado satisfactoriamente')
        return redirect(url_for('lista_usuarios'))
    
    return render_template('agregar_usuario.html')

# Ruta para mostrar la lista de usuarios
@app.route('/usuarios')
def lista_usuarios():
    usuarios = Usuarios.query.all()
    return render_template('lista_usuarios.html', usuarios=usuarios)


# Rutas para temas
@app.route('/temas')
def lista_temas():
    temas = Temas.query.all()
    return render_template('lista_temas.html', temas=temas)

@app.route('/agregar_tema', methods=['GET', 'POST'])
def agregar_tema():
    if request.method == 'POST':
        # Tomar los datos del formulario
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        id_usuario = request.form['id_usuario']  # Asumiendo que se pasa el id_usuario

        # Crear un nuevo objeto Tema
        nuevo_tema = Temas(
            titulo=titulo,
            descripcion=descripcion,
            id_usuario=id_usuario,
            fecha_creacion=datetime.now()  # Añadir la fecha actual
        )

        # Agregar el tema a la base de datos
        db.session.add(nuevo_tema)
        db.session.commit()

        # Redirigir a la vista del tema recién creado
        return redirect(url_for('ver_tema', id_tema=nuevo_tema.id))
    
    # Si el método es GET, simplemente mostrar el formulario
    return render_template('agregar_tema.html')


# Rutas para respuestas
@app.route('/temas/<int:id_tema>')
def ver_tema(id_tema):
    tema = Temas.query.get_or_404(id_tema)
    respuestas = Respuestas.query.filter_by(id_tema=id_tema).all()
    return render_template('ver_tema.html', tema=tema, respuestas=respuestas)

@app.route('/temas/<int:id_tema>/agregar_respuesta', methods=['POST'])
def agregar_respuesta(id_tema):
    if request.method == 'POST':
        contenido = request.form['contenido']
        id_usuario = request.form['id_usuario']  # Asegúrate de tener el id del usuario aquí

        # Crear un nuevo objeto Respuesta
        nueva_respuesta = Respuestas(
            id_tema=id_tema,
            id_usuario=id_usuario,
            contenido=contenido,
            fecha_respuesta=datetime.now()  # Añadir la fecha actual
        )

        # Agregar la respuesta a la base de datos
        db.session.add(nueva_respuesta)
        db.session.commit()

        flash('Respuesta agregada satisfactoriamente')
        return redirect(url_for('ver_tema', id_tema=id_tema))

#ver respuestas
@app.route('/temas/<int:id_tema>/ver_respuestas')
def ver_respuestas(id_tema):
    tema = Temas.query.get_or_404(id_tema)
    respuestas = Respuestas.query.filter_by(id_tema=id_tema).all()
    return render_template('ver_respuestas.html', tema=tema, respuestas=respuestas)



if __name__ == '__main__':
    app.run(debug=True)