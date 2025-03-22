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

# Ruta para la página de reservaciones (reservation.html).
@app.route('/reserva')
def reserva():
    return render_template('reservation.html')  # Renderiza la página HTML llamada 'reservation.html'.

# Ruta para la página de registro de usuarios (registrouser.html).
@app.route('/registro')
def registro():
    return render_template('registrouser.html')  # Renderiza la página HTML llamada 'registrouser.html'.

# Ruta para salir (redirige a la página principal).
@app.route('/exit')
def exit():
    return render_template('index.html')  # Renderiza nuevamente la página 'index.html'.

# Ruta para cancelar (cancelacion.html).
@app.route('/cancel')
def cancel():
    return render_template('cancelacion.html')  # Renderiza la página HTML llamada 'cancelacion.html'.

# Configuración para ejecutar la aplicación en modo depuración en el puerto 5000.
if __name__ == '__main__': 
    app.run(debug=True, port=5000)  # Ejecuta la app con depuración activa y en el puerto 5000.