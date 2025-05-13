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
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import mysql.connector  # Cambiado para usar mysql.connector
import smtplib


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
    nombre = session.get('nombre') if 'user_id' in session else None
    rol = session.get('rol') if 'user_id' in session else None

    if rol == 'Paciente':
        return render_template('index.html', nombre=nombre)
    return render_template('index.html')

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
            cursor.execute("""
                SELECT id_usuario, rol, nombre, primer_apellido, segundo_apellido
                FROM usuario 
                WHERE correo = %s AND contraseña = SHA2(%s, 256)
            """, (correo, password))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                session['user_id'] = user[0]
                session['rol'] = user[1]
                session['nombre'] = user[2]
                session['apellido1'] = user[3]
                session['apellido2'] = user[4]
                
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
@app.route('/api/registro', methods=['GET', 'POST'])
def api_registro():
    if request.method == 'GET':
        return render_template('newuser.html')
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se recibieron datos JSON"}), 400
    
    nombre = data.get('nombre')
    apellido1 = data.get('apellido1')
    apellido2 = data.get('apellido2')
    correo = data.get('correo')
    password = data.get('password')

    if not all([nombre, apellido1, apellido2, correo, password]):
        return jsonify({"error": "Faltan campos requeridos "}), 400
    
    conn = conectar_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SET @new_id_usuario = 0;")
            cursor.callproc('registro_usuario', (nombre, apellido1, apellido2, correo, password, '@new_id_usuario'))
            cursor.execute("SELECT @new_id_usuario;")
            new_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({
                "message": "Usuario registrado exitosamente",
                "id_usuario": new_id
            }), 201
        except mysql.connector.Error as err:
            return jsonify({"error": f"Error al insertar datos: {str(err)}"}), 500
    else:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

# Ruta para la página de registro de doctor (registrodoc.html).
@app.route('/api/newdoc', methods=['GET', 'POST'])
def api_newdoc():
    if request.method == 'GET':
        return render_template('newdoctor.html')
        
    data = request.get_json()
    if not data:
        return jsonify({"error": "Faltan campos requeridos "}), 400

    cedula = data.get('cedula')
    curp = data.get('curp')
    rfc = data.get('rfc')
    nombre = data.get('nombre')
    apellido1 = data.get('apellido1')
    apellido2 = data.get('apellido2')
    telefono = data.get('telefono')
    correo = data.get('correo')
    password = data.get('password')

    if not all([cedula, curp, rfc, nombre, apellido1, apellido2, telefono, correo, password]):
        return jsonify({"error": "Faltan campos requeridos "}), 400
        
    conn = conectar_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SET @new_id_doctor = 0;")
            cursor.callproc('registro_doctor', (nombre, apellido1, apellido2, correo, password, telefono, cedula, curp, rfc, '@new_id_doctor'))
            cursor.execute("SELECT @new_id_doctor;")
            new_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({
                "message": "Doctor registrado exitosamente",
                "id_usuario": new_id
            }), 201
        except mysql.connector.Error as err:
            return jsonify({"error": f"Error al insertar datos: {str(err)}"}), 500
    else:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

# Ruta para la página de reserva de cita (reservation.html).
@app.route('/api/reserva', methods=['GET', 'POST'])
def api_reserva():
    if request.method == 'GET':

        nombre = session.get('nombre')
        apellido1 = session.get('apellido1')
        apellido2 = session.get('apellido2')

        return render_template('reservation.html', nombre=nombre, apellido1=apellido1, apellido2=apellido2)

    if 'user_id' not in session:
        return jsonify({"error": "No autorizado. Inicia sesión."}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Faltan datos en la solicitud "}), 400
    
    curp = data.get('curp')
    edad = data.get('edad')
    telefono = data.get('telefono')
    alergias = data.get('alergias')
    discapacidad = data.get('discapacidad')
    fecha = data.get('fecha')
    horario = data.get('horarios')
    ubicacion = data.get('ubicacion')
    correo = data.get('correo')
    confirmacion = data.get('confirmacion')
        
    if correo != confirmacion:
        return jsonify({"error": "Los correos no coinciden"}), 400
    
    if not all([curp, edad, telefono, fecha, horario, ubicacion]):
        return jsonify({"error": "Faltan campos requeridos"}), 400
    
    nombre = session.get('nombre')
    apellido1 = session.get('apellido1')
    apellido2 = session.get('apellido2')

    if not all([nombre, apellido1]):
        return jsonify({"error": "No se pudieron obtener los datos del usuario"}), 400
        
    conn = conectar_db()
    if not conn:
        return jsonify({"error": "No se logro conectar con la base de datos"}), 500
    
    try:
        cursor = conn.cursor()

        query = """ 
            SELECT id_usuario FROM usuario
            WHERE nombre = %s AND primer_apellido = %s AND segundo_apellido = %s
        """
        cursor.execute(query, (nombre, apellido1, apellido2))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "Usuario no encontrado en la base de datos"}), 404
        
        id_usuario = result[0]

        cursor.callproc('insertar_cita', (
            id_usuario, curp, int(edad), telefono, alergias, discapacidad, fecha, horario, ubicacion
        ))

        conn.commit()
        return jsonify({"message": "Cita registrada exitosamente"}), 201
    
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": f"Error al registrar la cita: {str(err)}"}), 500
    
    finally:
        cursor.close()
        conn.close()

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