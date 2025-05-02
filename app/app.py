"""
Autores: 
Axel Castañeda Sánchez 
Antonio Albuerne Silva
Alyn Layla Nila Vélez
Luis Roberto Rodríguez Marroquin 
Sebastián Villaluz Martínez
Daniela Zuno Aguilar

Descripción:
Este archivo contiene el código para la creación de la aplicación web con Flask.
"""

# Importamos Flask y las funciones necesarias para manejar las rutas y plantillas HTML.
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector  # Cambiado para usar mysql.connector

# ---------------- CONEXIÓN A LA BASE DE DATOS ----------------
def conectar_db():  # Función para conectar a la base de datos
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Meliodas1.",  # Se ajusta según la configuración
            database="hospital",  # Nombre de la base de datos
        )
        print("✅ Conexión exitosa a la base de datos.")
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Error al conectar a la base de datos: {err}")
        return None

# Creamos una instancia de la aplicación Flask.
app = Flask(__name__)

app.secret_key = 'aL#9v@!fQz7k2Wm3T$xB1eNpLuY6rVc0'

# Ruta para la página principal (index.html).
@app.route('/')
def index():
    return render_template('index.html', nombre=session.get('nombre') if 'user_id' in session else None)

@app.route('/docindex')
def docindex():
    if 'user_id' in session and session.get('rol') == 'Doctor':
        return render_template('indexdoc.html', nombre=session.get('nombre'))
    return redirect(url_for('login'))

# Ruta para la página de login (login.html).
@app.route('/login', methods=['GET', 'POST'])
def login():
    if  request.method == 'POST':
        correo = request.form.get('usuario')
        password = request.form.get('contrasena')
        
        conn = conectar_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_usuario, rol, nombre FROM usuario WHERE correo = %s AND contraseña = SHA2(%s, 256)", (correo, password))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                session['user_id'] = user[0]
                session['rol'] = user[1]
                session['nombre'] = user[2]
                
                if user[1] == 'Paciente':
                    return redirect(url_for('index'))
                elif user[1] == 'Doctor':
                    return redirect(url_for('docindex'))
            else:
                return "Correo o contraseña incorrectos"
            
    return render_template('login.html')  # Renderiza la página HTML llamada 'login.html'.

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('rol', None)
    session.pop('nombre', None)
    
    return redirect(url_for('index'))

# Ruta para la página de registro de usuario (registrouser.html).
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido1 = request.form.get('apellido1')
        apellido2 = request.form.get('apellido2')
        correo = request.form.get('correo')
        password = request.form.get('password')

        conn = conectar_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SET @new_id_usuario = 0;")
                cursor.callproc('registro_usuario', (nombre, apellido1, apellido2, correo, password, '@new_id_usuario'))
                cursor.execute("SELECT @new_id_usuario;")
                new_id = cursor.fetchone()[0]
                print(f"🆕 Nuevo ID de usuario registrado: {new_id}")
                conn.commit()
                cursor.close()
                conn.close()
                return redirect(url_for('index'))
            except mysql.connector.Error as err:
                return f"❌ Error al insertar datos: {err}"

    return render_template('registrouser.html')  # Renderiza la página de registro de usuario.

# Ruta para la página de registro de doctor (registrodoc.html).
@app.route('/newdoc', methods=['GET', 'POST'])
def newdoc():
    if request.method == 'POST':
        cedula = request.form.get('cedula')
        curp = request.form.get('curp')
        rfc = request.form.get('rfc')
        nombre = request.form.get('nombre')
        apellido1 = request.form.get('apellido1')
        apellido2 = request.form.get('apellido2')
        telefono = request.form.get('telefono')
        correo = request.form.get('correo')
        password = request.form.get('password')
        
        conn = conectar_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SET @new_id_doctor = 0;")
                cursor.callproc('registro_doctor', (nombre, apellido1, apellido2, correo, password, telefono, cedula, curp, rfc, '@new_id_doctor'))
                cursor.execute("SELECT @new_id_doctor;")
                new_id = cursor.fetchone()[0]
                print(f"🆕 Nuevo ID de doctor registrado: {new_id}")
                conn.commit()
                cursor.close()
                conn.close()
                return redirect(url_for('index'))
            except mysql.connector.Error as err:
                return f"❌ Error al registrar al doctor: {err}"
            
    return render_template('newdoctor.html')  # Renderiza la página de registro de doctor.

# Ruta para la página de reserva de cita (reservation.html).
@app.route('/reserva', methods=['GET', 'POST'])
def reserva():
    if request.method == 'POST':
        curp = request.form.get('curp')
        edad = request.form.get('edad')
        telefono = request.form.get('telefono')
        alergias = request.form.get('alergias')
        discapacidad = request.form.get('discapacidad')
        fecha = request.form.get('fecha')
        horario = request.form.get('horarios')
        ubicacion = request.form.get('ubicacion')
        correo = request.form.get('correo')
        confirmacion = request.form.get('confirmacion')
        
        if correo != confirmacion:
            return "⚠️ Los correos no coinciden. Intenta de nuevo."
        
        conn = conectar_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.callproc('insertar_cita', (
                    curp, int(edad), telefono, alergias, discapacidad, fecha, horario, ubicacion
                    ))
                conn.commit()
                cursor.close()
                conn.close()
                return redirect(url_for('index'))
            except mysql.connector.Error as err:
                return f"❌ Error al registrar la cita: {err}"
 
    return render_template('reservation.html')

# Ruta para la página de métodos de pago (metodopago.html).
@app.route('/pago')
def pago():
    return render_template('metodopago.html')  # Renderiza la página de métodos de pago.

# Ruta para la página de búsqueda de archivo (busqueda.html).
@app.route('/file')
def file():
    opcion = request.args.get('opcion', '')  # Obtiene la opción seleccionada en la URL.
    return render_template('busqueda.html', opcion=opcion)  # Renderiza la página de búsqueda de archivo.

# Ruta para procesar la cita: modificación o cancelación dependiendo de la opción seleccionada.
@app.route('/procesar_cita', methods=['POST'])
def procesar_cita():
    folio = request.form.get('foliodecita')  # Obtiene el folio de la cita desde el formulario.
    opcion = request.form.get('opcion')  # Obtiene la opción seleccionada: modificación o cancelación.

    # Verificamos si se ingresó un folio.
    if not folio:
        return "Error: Debes ingresar un folio.", 400
    
    conn = conectar_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id_cita FROM cita WHERE id_cita = %s", (folio,))
            resultado = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if resultado:
                # Redirige a la página de modificación si la opción seleccionada es "modification".
                if opcion == "modification":
                    return redirect(url_for('modification', folio=folio))
                # Redirige a la página de cancelación si la opción seleccionada es "cancel".
                elif opcion == "cancel":
                    return redirect(url_for('cancel', folio=folio))  
                else:
                    return "Error: Opción no válida.", 400
            else:
                return "Error: El folio de cita no existe.", 404
        except mysql.connector.Error as err:
            return f"❌ Error al consultar la base de datos: {err}"
        
        return "Error: No se pudo conectar a la base de datos.", 500

@app.route('/pacient')
def pacient():
    return render_template('paciente.html')

# Ruta para la página de modificación de cita (modificacion.html).
@app.route('/modification')
def modification():
    folio = request.args.get('folio', '')  # Obtiene el folio de la cita desde la URL.
    return render_template('modificacion.html', folio=folio)

# Ruta para la página de cancelación de cita (cancelacion.html).
@app.route('/cancel')
def cancel():
    folio = request.args.get('folio', '')  # Obtiene el folio de la cita desde la URL.
    return render_template('cancelacion.html', folio=folio)

@app.route('/historial')
def historial():
    return render_template('historialcld.html')

# Si este archivo es ejecutado como principal, inicia la aplicación Flask en modo debug.
if __name__ == '__main__':  
    conectar_db()  # Ejecuta la conexión a la base de datos al iniciar
    app.run(debug=True)  # Ejecuta la aplicación Flask en modo debug para facilitar la depuración.