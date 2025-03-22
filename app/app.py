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

from flask import Flask, render_template, request, redirect, url_for  # Importamos Flask y render_template para manejar nuestra aplicación web.

app = Flask(__name__)  # Creamos una instancia de Flask.

# Ruta para la página principal (index.html).
@app.route('/')
def index():
    return render_template('index.html')  # Renderiza la página HTML llamada 'index.html'.

# Ruta para la página de login (login.html).
@app.route('/login')
def login():
    return render_template('login.html')  # Renderiza la página HTML llamada 'login.html'.

@app.route('/registro')
def registro():
    return render_template('registrouser.html')

@app.route('/newdoctor')
def newdoctor():
    return render_template('registrodoc.html')

@app.route('/reserva')
def reserva():
    return render_template('reservation.html')  # Renderiza la página HTML llamada 'reservation.html'.

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

# Ruta para salir (redirige a la página principal).
@app.route('/exit')
def exit():
    return render_template('index.html')  # Renderiza nuevamente la página 'index.html'.

if __name__ == '__main__': 
    app.run(debug=True)
