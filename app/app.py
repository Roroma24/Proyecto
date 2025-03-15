from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/reserva')
def reserva():
    return render_template('reservation.html')

@app.route('/registro')
def registro():
    return render_template('registrouser.html')

@app.route('/exit')
def exit():
    return render_template('index.html')

@app.route('/cancel')
def cancel():
    return render_template('cancelacion.html')

if __name__ == '__main__': 
    app.run(debug=True, port=5000)