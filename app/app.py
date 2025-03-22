<<<<<<< HEAD
from flask import Flask, render_template, request, redirect, url_for
=======
"""
Autores: 
Axel Castañeda Sánchez 
Antonio Albuerne Silva
Alyn Layla Nila Vélez
Luis Roberto Rodríguez Marroquin 
Sebastián Villaluz Martínez
Daniela Zuno Aguilar
>>>>>>> 643bdc13029ed472aaeefdc8c95fab140dd41c70

Descripción:
Este archivo contiene el código para la creación de la aplicación web con Flask.
"""

from flask import Flask, render_template  # Importamos Flask y render_template para manejar nuestra aplicación web.

app = Flask(__name__)  # Creamos una instancia de Flask.

# Ruta para la página principal (index.html).
@app.route('/')
def index():
    return render_template('index.html')  # Renderiza la página HTML llamada 'index.html'.

# Ruta para la página de login (login.html).
@app.route('/login')
def login():
    return render_template('login.html')  # Renderiza la página HTML llamada 'login.html'.

<<<<<<< HEAD
@app.route('/registro')
def registro():
    return render_template('registrouser.html')

@app.route('/newdoctor')
def newdoctor():
    return render_template('registrodoc.html')

=======
# Ruta para la página de reservaciones (reservation.html).
>>>>>>> 643bdc13029ed472aaeefdc8c95fab140dd41c70
@app.route('/reserva')
def reserva():
    return render_template('reservation.html')  # Renderiza la página HTML llamada 'reservation.html'.

<<<<<<< HEAD
@app.route('/pago')
def pago():
    return render_template('metodopago.html')

@app.route('/file')
def file():
    opcion = request.args.get('opcion', '')
    return render_template('busqueda.html')

@app.route('/procesar_cita', methods=['POST'])
def procesar_cita():
    folio = request.form.get('foliodecita')
    opcion = request.form.get('opcion')

    if not folio:
        return "Error: Debes ingresar un folio.", 400

    if opcion == "modification":
        return redirect(url_for('modification', folio=folio))
    elif opcion == "cancel":
        return redirect(url_for('cancel', folio=folio))
    else:
        return "Error: No se ha seleccionado una opción válida.", 400

@app.route('/modification')
def modification():
    folio = request.args.get('folio', '')
    return render_template('modificacion.html', folio=folio)

@app.route('/cancel')
def cancel():
    folio = request.args.get('folio', '')
    return render_template('cancelacion.html', folio=folio)
=======
# Ruta para la página de registro de usuarios (registrouser.html).
@app.route('/registro')
def registro():
    return render_template('registrouser.html')  # Renderiza la página HTML llamada 'registrouser.html'.
>>>>>>> 643bdc13029ed472aaeefdc8c95fab140dd41c70

# Ruta para salir (redirige a la página principal).
@app.route('/exit')
def exit():
    return render_template('index.html')  # Renderiza nuevamente la página 'index.html'.

<<<<<<< HEAD
if __name__ == '__main__': 
    app.run(debug=True)
=======
# Ruta para cancelar (cancelacion.html).
@app.route('/cancel')
def cancel():
    return render_template('cancelacion.html')  # Renderiza la página HTML llamada 'cancelacion.html'.

# Configuración para ejecutar la aplicación en modo depuración en el puerto 5000.
if __name__ == '__main__': 
    app.run(debug=True, port=5000)  # Ejecuta la app con depuración activa y en el puerto 5000.
>>>>>>> 643bdc13029ed472aaeefdc8c95fab140dd41c70
