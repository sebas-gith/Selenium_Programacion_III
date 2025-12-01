from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "programacion3"

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'biblioteca.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Libro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    anio = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()


@app.route('/')
def root():
    if not session.get('user'):
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        if usuario == "bibliotecario" and password == "admin123":
            session['user'] = usuario
            return redirect(url_for('dashboard'))
        else:
            flash("Credenciales inválidas", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not session.get('user'): return redirect(url_for('login'))
    libros = Libro.query.all()
    return render_template('dashboard.html', libros=libros)

@app.route('/agregar', methods=['POST'])
def agregar():
    if not session.get('user'): return redirect(url_for('login'))
    
    titulo = request.form['titulo']
    autor = request.form['autor']
    try:
        anio = int(request.form['anio'])
    except ValueError:
        flash("El año debe ser un número", "warning")
        return redirect(url_for('dashboard'))

    if anio < 1900 or anio > 2025:
        flash("Error: Año fuera de rango permitido (1900-2025)", "warning")
    else:
        nuevo_libro = Libro(titulo=titulo, autor=autor, anio=anio)
        db.session.add(nuevo_libro)
        db.session.commit()
        flash("Libro agregado correctamente", "success")
        
    return redirect(url_for('dashboard'))

@app.route('/eliminar/<int:id>')
def eliminar(id):
    if not session.get('user'): return redirect(url_for('login'))
    libro = Libro.query.get_or_404(id)
    db.session.delete(libro)
    db.session.commit()
    flash("Libro eliminado", "info")
    return redirect(url_for('dashboard'))

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if not session.get('user'): return redirect(url_for('login'))
    libro = Libro.query.get_or_404(id)
    
    if request.method == 'POST':
        nuevo_titulo = request.form['titulo']
        
        if not nuevo_titulo:
            flash("El título no puede estar vacío", "warning")
            return render_template('editar.html', libro=libro)

        libro.titulo = nuevo_titulo
        libro.autor = request.form['autor']
        libro.anio = int(request.form['anio'])
        db.session.commit()
        flash("Libro actualizado con éxito", "success")
        return redirect(url_for('dashboard'))
        
    return render_template('editar.html', libro=libro)

if __name__ == '__main__':
    app.run(debug=True, port=5000)