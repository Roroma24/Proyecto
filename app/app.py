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
from password_validator import PasswordValidator
from dotenv import load_dotenv
from datetime import datetime
import re
import os
import mysql.connector  
import smtplib
import calendar
import hashlib


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
    
load_dotenv()

# Creamos una instancia de la aplicación Flask.
app = Flask(__name__)
app.secret_key = os.getenv("secret_key")

password_valid = PasswordValidator()
password_valid \
    .min(8) \
    .max(14) \
    .has().uppercase() \
    .has().lowercase() \
    .has().symbols() \
    .no().spaces()

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
    
    data = {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}
    
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
    
    data = {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}
    
    nombre = data.get('nombre')
    apellido1 = data.get('apellido1')
    apellido2 = data.get('apellido2')
    correo = data.get('correo')
    password = data.get('password')

    if not all([nombre, apellido1, apellido2, correo, password]):
        return jsonify({"error": "Faltan campos requeridos "}), 400
    
    if not password_valid.validate(password):
        return jsonify({"error": "La contraseña debe tener al menos 8 caracteres, una mayúscula, una minuscula y un simbolo especial."}), 400
    
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
        return jsonify({"error": "No se recibieron datos JSON"}), 400
    
    data = {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}

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
    
    if not password_valid.validate(password):
        return jsonify({"error": "La contraseña debe tener al menos 8 caracteres, una mayúscula, una minuscula y un simbolo especial."}), 400
        
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

    data = {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}

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

    if not all([nombre, apellido1, apellido2, curp, edad, telefono, alergias, discapacidad, fecha, horarios, ubicacion, especialidad_nombre]):
        return jsonify({"error": "Faltan campos requeridos "}), 400

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
        args = (
            id_usuario, curp, edad, telefono, alergias, discapacidad, fecha, horarios, ubicacion, id_especialidad, 0
        )

        result = cursor.callproc('insertar_cita', args)

        id_cita = result[-1]

        if not id_cita:
            return jsonify({"error": "No se pudo obtener el ID de la cita"}), 500

        session['id_cita'] = id_cita

        db.commit()

        return jsonify({"message": "Cita reservada correctamente", "redirect": url_for('api_pago')})
    except mysql.connector.Error as err:
        return jsonify({"error": f"Error al insertar cita: {err}"}), 500
    finally:
        cursor.close()
        db.close()

# Ruta para la página de métodos de pago (metodopago.html).
@app.route('/api/pago', methods=['GET', 'POST'])
def api_pago():
    if request.method == 'GET':
        return render_template('metodopago.html')  # Renderiza la página de búsqueda de archivo.
    
    if 'id_usuario' not in session:
        return jsonify({"error": "Debes iniciar sesión para buscar cita"}), 401
    
    id_usuario = session['id_usuario']

    data = request.get_json()

    if not data:
        return jsonify({"error": "No se recibieron datos JSON"}), 400

    data = {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}
    
    nombre = data.get('nombre')
    apellido1 = data.get('apellido1')
    apellido2 = data.get('apellido2')
    ubicacion = data.get('ubicacion')
    cuenta = data.get('cuenta')
    correo = data.get('correo')
    concepto = data.get('concepto')
    monto = data.get('monto')
    metodo = data.get('metodo')

    if not all([nombre, apellido1, apellido2, ubicacion, cuenta, correo, concepto, monto, metodo]):
        return jsonify({"error": "Faltan campos requeridos "}), 400

    db = conectar_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT id_usuario
        FROM usuario
        WHERE nombre = %s AND primer_apellido = %s AND segundo_apellido = %s AND correo = %s
    """, (nombre, apellido1, apellido2, correo))

    user = cursor.fetchone()

    if not user:
        return jsonify({"error": "Usuario con ese nombre no está registrado"}), 404
    
    id_usuario_db = user[0]
    if id_usuario != id_usuario_db:
        return jsonify({"error": "Los datos no coinciden con el usuario autenticado"}), 403
    
    cursor.execute("""
        SELECT id_clinica
        FROM sucursal
        WHERE direccion = %s
    """, (ubicacion,))

    ubi = cursor.fetchone()

    if not ubi:
        return jsonify({"error": "La ubicación no coincide con la seleccionada anteriormente."}), 404
    
    id_cita = session.get('id_cita')

    if not id_cita:
        return jsonify({"error": "No se encontró la cita reservada para el pago."}), 404
    
    try:
        cursor.callproc('registrar_pago', (
            concepto, monto, metodo, cuenta, id_cita
        ))

        for result in cursor.stored_results():
            result.fetchall()
            
        db.commit()
        return jsonify({"message": "Pago exitoso", "redirect": url_for('api_index')})
    except mysql.connector.Error as err:
        return jsonify({"error": f"Error al procesar el pago: {err}"}), 500
    finally:
        cursor.close()
        db.close()

# Ruta para la página de búsqueda de archivo (busqueda.html).
@app.route('/api/file', methods=['GET', 'POST'])
def api_file():
    if request.method == 'GET':
        return render_template('busqueda.html')  # Renderiza la página de búsqueda de archivo.
    
    if 'id_usuario' not in session:
        return jsonify({"error": "Debes iniciar sesión para buscar cita"}), 401
    
    id_usuario = session['id_usuario']
    opcion = session['opcion']

    data = request.get_json()

    if not data:
        return jsonify({"error": "No se recibieron datos JSON"}), 400
    
    nombre = data.get('nombres')
    apellido1 = data.get('primerapellido')
    apellido2 = data.get('segundoapellido')
    correo = data.get('correo')
    folio = data.get('foliodecita')

    if not all([nombre, apellido1, apellido2, correo, folio]):
        return jsonify({"error": "Faltan campos requeridos "}), 400

    opcion = session.get('opcion')

    if not opcion:
        return jsonify({"error": "No se especificó una opción válida"}), 400
    
    db = conectar_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT id_usuario
        FROM usuario
        WHERE nombre = %s AND primer_apellido = %s AND segundo_apellido = %s AND correo = %s
    """, (nombre, apellido1, apellido2, correo))

    us = cursor.fetchone()

    if not us:
        return jsonify({"error": "Usuario con ese nombre no está registrado"}), 404

    id_usuario_db = us[0]
    if id_usuario != id_usuario_db:
        return jsonify({"error": "Los datos no coinciden con el usuario autenticado"}), 403

    cursor.execute("""
        SELECT id_cita
        FROM cita
        WHERE id_cita = %s
    """, (folio,))

    ci = cursor.fetchone()

    cursor.close()
    db.close()

    if not ci:
        return jsonify({"error": "No se encontraron citas con ese folio"}), 404

    folio = ci[0]
    session['folio'] = folio

    if opcion == "modification":
        return jsonify({"redirect": url_for('api_modification', folio = folio)})
    elif opcion == "cancel":
        return jsonify({"redirect": url_for('api_cancel', folio = folio)})
    else:
        return jsonify({"error": "Opción no válida"}), 400

# Ruta para procesar la cita: modificación o cancelación dependiendo de la opción seleccionada.
@app.route('/api/procesar_cita', methods=['POST'])
def api_procesar_cita():
    
    opcion = request.form.get('opcion')

    if opcion not in ['modification', 'cancel']:
        return "Error: Opción no válida.", 400

    session['opcion'] = opcion

    return redirect(url_for('api_file'))

# Ruta para la página de búsqueda de paciente.
@app.route('/api/pacient', methods=['GET', 'POST'])
def api_pacient():
    if request.method == 'GET':
        return render_template('paciente.html')

    data = request.get_json()
    if not data:
        return jsonify({"error": "Faltan campos requeridos "}), 400

    idpaciente = data.get('id_paciente')

    if not idpaciente:
        return jsonify({"error": "Faltan campos requeridos"}), 400
    
    conn = conectar_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.nombre, u.primer_apellido, u.segundo_apellido, p.edad, u.correo, p.curp, p.alergias, p.discapacidad
                FROM paciente p
                JOIN usuario u ON p.id_usuario = u.id_usuario
                WHERE p.id_paciente = %s
            """, (idpaciente,))
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
        return render_template('modificacion.html')
    
    if 'id_usuario' not in session:
        return jsonify({"error": "Debes iniciar sesión para modificar una cita"}), 401

    id_usuario = session['id_usuario']
    folio = session['folio']

    data = request.get_json()
    if not data:
        return jsonify({"error": "No se recibieron datos JSON"}), 400

    data = {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}

    nombre = data.get('nombre')
    apellido1 = data.get('apellido1')
    apellido2 = data.get('apellido2')
    edad_str = data.get('edad')
    if not edad_str:
        return jsonify({"error": "Edad es un campo obligatorio"}), 400
    try:
        edad = int(edad_str)
    except ValueError:
        return jsonify({"error": "Edad debe ser un número válido"}), 400
    telefono = data.get('telefono')
    correo = data.get('correo')
    discapacidad = data.get('discapacidad')
    alergias = data.get('alergias')
    horarios = data.get('horarios', '')
    try:
        datetime.strptime(str(horarios), '%H:%M')
    except ValueError:
        return jsonify({"error": "Horario debe tener el formato válido HH:MM, por ejemplo '09:00'"}), 400
    especialidad_nombre = data.get('especialidad')
    direccion = data.get('ubicacion')
    fecha = data.get('fecha')
    try:
        datetime.strptime(fecha, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "La fecha debe tener el formato YYYY-MM-DD"}), 400
    
    if not all([nombre, apellido1, apellido2, edad_str, telefono, correo, discapacidad, alergias, horarios, especialidad_nombre, direccion, fecha]):
        return jsonify({"error": "Faltan campos requeridos "}), 400

    db = conectar_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT u.id_usuario
        FROM usuario u
        JOIN paciente p ON u.id_usuario = p.id_usuario
        WHERE u.nombre = %s AND u.primer_apellido = %s AND u.segundo_apellido = %s AND u.correo = %s AND p.edad = %s
    """, (nombre, apellido1, apellido2, correo, edad))

    user = cursor.fetchone()

    if not user:
        return jsonify({"error": "Nombre, correo o edad del usuario incorrectos"}), 404
    
    id_user_db = user[0]
    if id_usuario != id_user_db:
        return jsonify({"error": "Los datos no coinciden con el usuario autenticado"}), 403
    
    cursor.execute("SELECT id_especialidad FROM especialidad WHERE nombre_especialidad = %s", (especialidad_nombre,))
    especialidad = cursor.fetchone()
    if not especialidad:
        return jsonify({"error": "Especialidad no registrada"}), 400
    
    id_especialidad = especialidad[0]

    try:
        cursor.callproc('modificar_cita', (
            folio, fecha, horarios, telefono, alergias, direccion, id_especialidad, discapacidad
        ))
        db.commit()
        return jsonify({"message": "Cita modificada correctamente", "redirect": url_for('api_exit')}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": f"Error al modificar cita: {err}"}), 500
    finally:
        cursor.close()
        db.close()

# Ruta para la página de cancelación de cita (cancelacion.html).
@app.route('/api/cancel', methods=['GET', 'POST'])
def api_cancel():
    if request.method == 'GET':
        return render_template('cancelacion.html')
    
    if 'id_usuario' not in session:
        return jsonify({"error": "Debes iniciar sesión para modificar una cita"}), 401

    id_usuario = session['id_usuario']
    folio = session['folio']

    data = request.get_json()
    if not data:
        return jsonify({"error": "No se recibieron datos JSON"}), 400
    
    data = {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}

    nombre = data.get('nombre')
    apellido1 = data.get('apellido1')
    apellido2 = data.get('apellido2')
    telefono = data.get('telefono')
    edad_str = data.get('edad')
    if not edad_str:
        return jsonify({"error": "Edad es un campo obligatorio"}), 400
    try:
        edad = int(edad_str)
    except ValueError:
        return jsonify({"error": "Edad debe ser un número válido"}), 400
    correo = data.get('correo')
    horarios = data.get('horarios', '')
    try:
        datetime.strptime(str(horarios), '%H:%M')
    except ValueError:
        return jsonify({"error": "Horario debe tener el formato válido HH:MM, por ejemplo '09:00'"}), 400
    fecha = data.get('fecha')
    try:
        datetime.strptime(fecha, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "La fecha debe tener el formato YYYY-MM-DD"}), 400

    if not all([nombre, apellido1, apellido2, telefono, edad_str, correo, horarios, fecha]):
        return jsonify({"error": "Faltan campos requeridos"}), 400
    
    db = conectar_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT u.id_usuario
        FROM usuario u
        JOIN paciente p ON u.id_usuario = p.id_usuario
        WHERE u.nombre = %s AND u.primer_apellido = %s AND u.segundo_apellido = %s AND u.correo = %s AND p.edad = %s AND p.telefono = %s
    """, (nombre, apellido1, apellido2, correo, edad, telefono))

    user = cursor.fetchone()

    if not user:
        return jsonify({"error": "Nombre, correo o edad del usuario incorrectos"}), 404
    
    id_user_db = user[0]
    if id_usuario != id_user_db:
        return jsonify({"error": "Los datos no coinciden con el usuario autenticado"}), 403
    
    cursor.execute("""
        SELECT id_cita
        FROM cita
        WHERE horario = %s AND fecha_cita = %s
    """, (horarios, fecha))

    cit = cursor.fetchone()

    if not cit:
        return jsonify({"error": "Fecha u hora no coincide"}), 404
    
    try:
        cursor.callproc('eliminar_cita', (
            folio,
        ))
        db.commit()
        return jsonify({"message": "Cita cancelada exitosamente", "redirect": url_for('api_exit')}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": f"Error al modificar cita: {err}"}), 500
    finally:
        cursor.close()
        db.close()

# Ruta para la página de historial de citas (historial.html).
@app.route('/api/historial', methods=['GET', 'POST'])
def api_historial():
    if request.method == 'GET':
        return render_template('historialcld.html')

    data = request.get_json()
    id_paciente = data.get('id_paciente') if data else None

    if not id_paciente:
        # Si no se envía, usa el usuario de la sesión (opcional)
        id_usuario = session.get('id_usuario')
        if not id_usuario:
            return jsonify({"error": "Debes iniciar sesión"}), 401
        query = "SELECT id_cita, hora, fecha FROM cita WHERE id_usuario = %s ORDER BY fecha DESC"
        params = (id_usuario,)
    else:
        # RELACIÓN DIRECTA POR id_paciente
        query = """
            SELECT id_cita, hora, fecha
            FROM cita
            WHERE id_paciente = %s
            ORDER BY fecha DESC
        """
        params = (id_paciente,)

    conn = conectar_db()
    if not conn:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        citas = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify([
            {"id_cita": row[0], "hora": row[1], "dia": row[2]}
            for row in citas
        ])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/exit')
def api_exit():
    rol = session.get('rol')
    if rol == 'Paciente':
        return redirect(url_for('api_index'))
    elif rol == 'Doctor':
        return redirect(url_for('api_docindex'))
    else:
        return redirect(url_for('api_logout'))

# Si este archivo es ejecutado como principal, inicia la aplicación Flask en modo debug.
if __name__ == '__main__':  
    conectar_db()  # Ejecuta la conexión a la base de datos al iniciar
    app.run(debug=True)  # Ejecuta la aplicación Flask en modo debug para facilitar la depuración.