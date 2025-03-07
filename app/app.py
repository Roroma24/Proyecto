from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
   cursos = ['PHP', 'Python', 'Java', 'Kotlin', 'Dart', 'JavaScript']
   data = {
       'titulo': 'Index123',
       'bienvenida': '¡Saludos!',
       'cursos': cursos,
       'numero_cursos': len(cursos)
   }
   return render_template('index.html', data=data)

@app.route('/inicio')
def inicio():
   return render_template('inicio.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)

