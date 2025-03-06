from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
   # Creación de un diccionario
   # Este diccionario puede mandar sus valores al index.html
   cursos = ['PHP', 'Python', 'Java', 'Kotlin', 'Dart', 'JavaScript']
   data={
       'titulo':'Index123',
       'bienvenida':'Saludos!',
       'cursos':cursos,
       'numero_cursos': len(cursos)
   }
   return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

