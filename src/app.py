# src/app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from src.models import User
from src.database import close_mongo_client, get_db # Importa get_db también
import os

app = Flask(__name__, template_folder='../templates') # Flask busca plantillas en la carpeta 'templates'
app.secret_key = os.urandom(24) # Necesario para la gestión de sesiones en Flask

# --- Rutas de la aplicación ---

@app.route('/')
def home():
    # Si el usuario ya está logueado, redirige a la página principal (index.html)
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login')) # Si no está logueado, redirige al login

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.find_by_username(username)

        if user and User.verify_password(user['password'], password):
            session['username'] = user['usuario'] # Guarda el username en la sesión
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(url_for('dashboard')) # Redirige a la página de éxito
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
            return render_template('login.html') # Vuelve a mostrar el formulario de login

    return render_template('login.html') # Muestra el formulario de login en GET

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        celular = request.form['celular']
        email = request.form['email']
        usuario = request.form['usuario']
        password = request.form['password']

        # Intenta crear el usuario
        user_id = User.create(nombre, apellido, celular, email, usuario, password)

        if user_id:
            flash(f"Usuario '{usuario}' registrado exitosamente. ¡Ahora puedes iniciar sesión!", 'success')
            return redirect(url_for('login')) # Redirige al login después de un registro exitoso
        else:
            # El mensaje de error ya se imprime dentro de User.create
            flash('Error al registrar usuario. Intenta con otro nombre de usuario o correo.', 'danger')
            return render_template('registrar_usuario.html') # Vuelve a mostrar el formulario de registro

    return render_template('registrar_usuario.html') # Muestra el formulario de registro en GET

@app.route('/dashboard')
def dashboard():
    # Protege esta ruta: solo accesible si el usuario está logueado
    if 'username' not in session:
        flash('Debes iniciar sesión para acceder a esta página.', 'warning')
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username']) # Muestra la página de éxito

@app.route('/logout')
def logout():
    session.pop('username', None) # Elimina el username de la sesión
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('login')) # Redirige al login

# Para cerrar la conexión de MongoDB cuando la aplicación Flask se apaga
@app.teardown_appcontext
def teardown_db(exception):
    close_mongo_client()

if __name__ == '__main__':
    # Asegúrate de que la colección 'usuario' esté lista (opcional, se creará al insertar)
    # También puedes asegurar la conexión inicial aquí si lo deseas
    try:
        # Esto solo asegura que se intente conectar al inicio
        # No es estrictamente necesario ya que get_db se llama al primer uso
        print("Preparando la aplicación Flask...")
        get_db().command("ping") # Intenta una operación simple para verificar conexión
    except Exception as e:
        print(f"La aplicación no pudo conectar a MongoDB al inicio: {e}")
        print("Asegúrate de que MongoDB esté corriendo y la URI en .env sea correcta.")
        # Podrías decidir salir si la conexión es crítica al inicio
        # import sys
        # sys.exit(1)
    app.run(debug=True) # debug=True recarga el servidor automáticamente y muestra errores detallados