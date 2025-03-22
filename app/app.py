from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/registro')
def registro():
    return render_template('registrouser.html')

@app.route('/newdoctor')
def newdoctor():
    return render_template('registrodoc.html')

@app.route('/reserva')
def reserva():
    return render_template('reservation.html')

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

@app.route('/exit')
def exit():
    return render_template('index.html')

if __name__ == '__main__': 
    app.run(debug=True)