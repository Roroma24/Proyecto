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
from dotenv import load_dotenv
from datetime import datetime
import re
import os
import mysql.connector  # Cambiado para usar mysql.connector
import smtplib
import calendar
import hashlib


# ---------------- CONEXIÓN A LA BASE DE DATOS ----------------
def conectar_db():  # Función para conectar a la base de datos
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Ror@$2405",  # Se ajusta según la configuración
            database="hospital",  # Nombre de la base de datos
        )
        print("✅ Conexión exitosa a la base de datos.")
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Error al conectar a la base de datos: {err}")
        return None
    
load_dotenv()

# Creamos una instancia de la aplicación Flask.
app = Flask(__name__)
app.secret_key = os.getenv("secret_key")

# Ruta para la página principal (index.html).
@app.route('/api/index')
def api_index():
    nombre = session.get('nombre') if 'id_usuario' in session else None
    rol = session.get('rol') if 'id_usuario' in session else None

    if rol == 'Paciente':
        return render_template('index.html', nombre=nombre)
    return render_template('index.html')

@app.route('/api/docindex')
def api_docindex():
    if 'id_usuario' in session and session.get('rol') == 'Doctor':
        return render_template('indexdoc.html', nombre=session.get('nombre'))
    return redirect(url_for('api_login'))

# Ruta para la página de login (login.html).
@app.route('/api/login', methods=['GET', 'POST'])
def api_login():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se recibieron datos JSON"}), 400
    
    correo = data.get('usuario')
    contrasena = data.get('contrasena')

    if not correo or not contrasena:
        return jsonify({'error': 'Faltan datos'}), 400

    hashed_password = hashlib.sha256(contrasena.encode()).hexdigest()

    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id_usuario, nombre, rol
        FROM usuario
        WHERE correo = %s AND contraseña = %s
    """, (correo, hashed_password))
    res = cursor.fetchone()

    cursor.close()
    conn.close()

    if res:
        id_usuario, nombre, rol = res

        session['id_usuario'] = id_usuario
        session['nombre'] = nombre
        session['rol'] = rol

        return jsonify({'message': 'Inicio de sesion exitoso', 'rol': rol}), 200
    else:
        return jsonify({'error': 'Correo o contraseña incorrectos'}), 401

@app.route('/api/logout')
def api_logout():
    session.clear()
    return redirect(url_for('api_index'))

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
            cursor.execute("SELECT id_usuario FROM usuario WHERE correo = %s", (correo,))
            if cursor.fetchone():
                return jsonify({"error": "El correo ya está registrado"}), 409
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
    especialidad = data.get('especialidad')
    curp = data.get('curp')
    rfc = data.get('rfc')
    nombre = data.get('nombre')
    apellido1 = data.get('apellido1')
    apellido2 = data.get('apellido2')
    telefono = data.get('telefono')
    correo = data.get('correo')
    password = data.get('password')

    if not all([cedula, especialidad, curp, rfc, nombre, apellido1, apellido2, telefono, correo, password]):
        return jsonify({"error": "Faltan campos requeridos "}), 400
        
    conn = conectar_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id_usuario FROM usuario WHERE correo = %s", (correo,))
            if cursor.fetchone():
                return jsonify({"error": "El correo ya está registrado"}), 409
            cursor.execute("SET @new_id_doctor = 0;")
            cursor.callproc('registro_doctor', (nombre, apellido1, apellido2, correo, password, telefono, cedula, curp, rfc, especialidad, '@new_id_doctor'))
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
        return render_template('reservation.html')
    
    if 'id_usuario' not in session:
        return jsonify({"error": "Debes iniciar sesión para reservar"}), 401
    
    id_usuario = session['id_usuario']
    data = request.get_json()

    nombre = data.get('nombre')
    apellido1 = data.get('apellido1')
    apellido2 = data.get('apellido2')

    curp = data.get('curp')
    edad_str = data.get('edad')
    if not edad_str:
        return jsonify({"error": "Edad es un campo obligatorio"}), 400
    try:
        edad = int(edad_str)
    except ValueError:
        return jsonify({"error": "Edad debe ser un número válido"}), 400

    telefono = data.get('telefono')
    alergias = data.get('alergias')
    discapacidad = data.get('discapacidad')
    fecha = data.get('fecha')
    horarios = data.get('horarios', '')
    try:
        datetime.strptime(str(horarios), '%H:%M')
    except ValueError:
        return jsonify({"error": "Horario debe tener el formato válido HH:MM, por ejemplo '09:00'"}), 400
    ubicacion = data.get('ubicacion')
    especialidad_nombre = data.get('especialidad')

    db = conectar_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT id_usuario
        FROM usuario
        WHERE nombre = %s AND primer_apellido = %s AND segundo_apellido = %s
    """, (nombre, apellido1, apellido2))

    us = cursor.fetchone()

    if not us:
        return jsonify({"error": "Usuario con ese nombre no está registrado"}), 404
    
    id_usuario_db = us[0]
    if id_usuario != id_usuario_db:
        return jsonify({"error": "Los datos no coinciden con el usuario autenticado"}), 403

    cursor.execute("SELECT id_especialidad FROM especialidad WHERE nombre_especialidad = %s", (especialidad_nombre,))
    especialidad = cursor.fetchone()
    if not especialidad:
        return jsonify({"error": "Especialidad no registrada"}), 400
    
    id_especialidad = especialidad[0]

    try:
        cursor.callproc('insertar_cita', (
            id_usuario, curp, edad, telefono, alergias, discapacidad,
            fecha, horarios, ubicacion, id_especialidad
        ))
        db.commit()
        return jsonify({"message": "Cita reservada correctamente", "redirect": url_for('pago')})
    except mysql.connector.Error as err:
        return jsonify({"error": f"Error al insertar cita: {err}"}), 500
    finally:
        cursor.close()
        db.close()

# Ruta para la página de métodos de pago (metodopago.html).
@app.route('/pago')
def pago():
    return render_template('metodopago.html')  # Renderiza la página de métodos de pago.

# Ruta para la página de búsqueda de archivo (busqueda.html).
@app.route('/api/file', methods=['GET', 'POST'])
def api_file():
    if request.method == 'GET':
        opcion = request.args.get('opcion', '')  # Obtiene la opción seleccionada en la URL.
        return render_template('busqueda.html', opcion=opcion)  # Renderiza la página de búsqueda de archivo.
    
    if 'id_usuario' not in session:
        return jsonify({"error": "Debes iniciar sesión para buscar cita"}), 401
    
    id_usuario = session['id_usuario']
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se recibieron datos JSON"}), 400
    
    nombre = data.get('nombre')
    apellido1 = data.get('apellido1')
    apellido2 = data.get('apellido2')
    correo = data.get('correo')
    opcion = data.get('opcion')  # <-- Recibe la opción (modification/cancel)
    
    db = conectar_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT id_usuario
        FROM usuario
        WHERE nombre = %s AND primer_apellido = %s AND segundo_apellido = %s AND correo = %s
    """, (nombre, apellido1, apellido2, correo))

    us = cursor.fetchone()

    if not us:
        cursor.close()
        db.close()
        return jsonify({"error": "Usuario con ese nombre no está registrado"}), 404

    id_usuario_db = us[0]
    if id_usuario != id_usuario_db:
        cursor.close()
        db.close()
        return jsonify({"error": "Los datos no coinciden con el usuario autenticado"}), 403

    cursor.execute("""
        SELECT id_cita
        FROM cita
        WHERE id_usuario = %s
    """, (id_usuario,))

    ci = cursor.fetchone()

    cursor.close()
    db.close()

    if not ci:
        return jsonify({"error": "No se encontraron citas con ese folio"}), 404

    folio = ci[0]

    if opcion == "modification":
        return redirect(url_for('api_modification', folio=folio))
    elif opcion == "cancel":
        return redirect(url_for('api_cancel', folio=folio))
    else:
        return jsonify({"error": "Opción no válida"}), 400

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
                    return redirect(url_for('api_modification', folio=folio))
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

@app.route('/api/pacient', methods=['GET', 'POST'])
def api_pacient():
    if request.method == 'GET':
        return render_template('paciente.html')

    data = request.get_json()
    if not data:
        return jsonify({"error": "Faltan campos requeridos "}), 400

    idpaciente = data.get('idpaciente')

    if not all([idpaciente]):
        return jsonify({"error": "Faltan campos requeridos"}), 400
    
    conn = conectar_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM paciente WHERE idpaciente = %s", (idpaciente,))
            paciente = cursor.fetchone()
            if paciente:
                return jsonify({
                    "nombre": paciente[0],
                    "primer_apellido": paciente[1],
                    "segundo_apellido": paciente[2],
                    "edad": paciente[3],
                    "correo": paciente[4],
                    "curp": paciente[5],
                    "alergias": paciente[6],
                    "discapacidad": paciente[7]
                    
                })
            else:
                return jsonify({"error": "Paciente no encontrado"}), 404
        finally:
            conn.close()
    else:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500



# Ruta para la página de modificación de cita (modificacion.html).
@app.route('/api/modification', methods=['GET', 'POST'])
def api_modification():
    if request.method == 'GET':
        folio = request.args.get('folio', '')
        return render_template('modificacion.html', folio=folio)

    if 'id_usuario' not in session:
        return jsonify({"error": "Debes iniciar sesión para modificar una cita"}), 401

    id_usuario = session['user_id']

    data = request.get_json()
    if not data:
        return jsonify({"error": "No se recibieron datos JSON"}), 400

    nombre = data.get('nombre')
    apellido1 = data.get('apellido1')
    apellido2 = data.get('apellido2')
    folio = data.get('folio')

    fecha_cita = data.get('fecha_cita')
    horario = data.get('horario')
    telefono = data.get('telefono')
    alergias = data.get('alergias')
    direccion = data.get('direccion')
    especialidad = data.get('especialidad')

    if not all([nombre, apellido1, apellido2, folio, fecha_cita, horario, telefono, alergias, direccion, especialidad]):
        return jsonify({"error": "Faltan campos requeridos"}), 400

    try:
        folio = int(folio)
    except ValueError:
        return jsonify({"error": "Folio inválido"}), 400

    conn = conectar_db()
    if not conn:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    try:
        cursor = conn.cursor()

        cursor.callproc('modificar_cita', (
            folio,
            fecha_cita,
            horario,
            telefono,
            alergias,
            direccion,
            especialidad
        ))
        conn.commit()
        return jsonify({"message": "Cita modificada exitosamente"}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": f"Error al modificar la cita: {err}"}), 500

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Ruta para la página de cancelación de cita (cancelacion.html).
@app.route('/api/cancel', methods=['GET', 'POST'])
def api_cancel():
    if request.method == 'GET':
        folio = request.args.get('folio', '')
        return render_template('cancelacion.html', folio=folio)

    if 'id_usuario' not in session:
        return jsonify({"error": "Debes iniciar sesión para cancelar una cita"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "No se recibieron datos JSON"}), 400

    nombre = data.get('nombre')
    apellido1 = data.get('apellido1')
    apellido2 = data.get('apellido2')
    folio = data.get('folio')

    if not all([nombre, apellido1, apellido2, folio]):
        return jsonify({"error": "Faltan campos requeridos"}), 400

    conn = conectar_db()
    if not conn:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id_usuario
            FROM usuario
            WHERE nombre = %s AND primer_apellido = %s AND segundo_apellido = %s
        """, (nombre, apellido1, apellido2))
        us = cursor.fetchone()
        if not us:
            cursor.close()
            conn.close()
            return jsonify({"error": "Usuario con ese nombre no está registrado"}), 404

        id_usuario_db = us[0]
        if session['user_id'] != id_usuario_db:
            cursor.close()
            conn.close()
            return jsonify({"error": "Los datos no coinciden con el usuario autenticado"}), 403

        cursor.execute("""
            SELECT id_cita FROM cita WHERE id_cita = %s AND id_usuario = %s
        """, (folio, id_usuario_db))
        cita = cursor.fetchone()
        if not cita:
            cursor.close()
            conn.close()
            return jsonify({"error": "No se encontró la cita para este usuario"}), 404

        cursor.callproc('eliminar_cita', (int(folio),))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Cita cancelada exitosamente"}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": f"Error al cancelar la cita: {err}"}), 500

@app.route('/historial')
def historial():
    return render_template('historialcld.html')

# Si este archivo es ejecutado como principal, inicia la aplicación Flask en modo debug.
if __name__ == '__main__':  
    conectar_db()  # Ejecuta la conexión a la base de datos al iniciar
    app.run(debug=True)  # Ejecuta la aplicación Flask en modo debug para facilitar la depuración.