# Sistema de Gestión Hospital Qualitas

## Introducción

Este repositorio contiene la arquitectura backend del Sistema de Gestión Hospital Qualitas, una plataforma web desarrollada en Flask que permite gestionar citas médicas, registrar usuarios, procesar pagos y otras funcionalidades administrativas propias de un entorno hospitalario.

## Autores

- Axel Castañeda Sánchez  
- Antonio Albuerne Silva  
- Alyn Layla Nila Vélez  
- Luis Roberto Rodríguez Marroquín  
- Sebastián Villaluz Martínez  
- Daniela Zuno Aguilar  

## Descripción General

El sistema está construido utilizando **Flask** como framework web principal, y **MySQL** como sistema de gestión de base de datos. Algunas de las funcionalidades clave incluyen:

- Registro y autenticación de usuarios (pacientes y médicos)
- Reserva, modificación y cancelación de citas médicas
- Procesamiento de pagos
- Gestión de sesiones y roles
- Validación y manejo de errores robusto

## Tecnologías Utilizadas

- **Backend:** Flask (Python)  
- **Base de Datos:** MySQL  
- **Frontend:** HTML, CSS, JavaScript  
- **Comunicación Cliente-Servidor:** AJAX, JSON  
- **ORM/Conexión:** mysql-connector-python  
- **Control de versiones:** Git  

---

## Proceso de Instalación

1. Clona el Repositorio desde Github.

```bash
git clone https://github.com/Roroma24/Proyecto.git
cd Proyecto/Proyecto
```

2. Crea y activa un entorno virtual (opcional pero altamente recomendado).

### Activación del entorno virtual:

```bash
python -m venv env
```

### En Windows:

```bash
env\Scripts\activate
```

### En Linux/Mac:
```bash
source env/bin/activate
```

3. Instala las dependencias con Python.

```bash
pip install flask mysql-connector-python python-dotenv password-validator
```

4. Crea un archivo .env en app con el siguiente contenido:

```bash
DB_HOST=localhost
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_NAME=nombre_base_de_datos
secret_key=alguna_clave_secreta
```

5. Inicializa la base de datos.

Ejecuta el script SQL que está en app/Database/base.sql en tu servidor MySQL para crear las tablas y procedimientos necesarios.

6. Ejecuta la aplicación.

```bash
cd app
python app.py
```

---

## Estructura del Backend

```
/Proyecto
│
├── app.py                # Archivo principal de la aplicación Flask
├── db.py                 # Conexión y utilidades de base de datos
├── static/               # Archivos estáticos (CSS, JS, imágenes)
├── templates/            # Plantillas HTML (Jinja2)
├── requirements.txt      # Dependencias del proyecto
└── ...
```

### Conexión a la Base de Datos

Se utiliza `mysql-connector-python` para manejar la conexión mediante la función `conectar_db()`, la cual proporciona mensajes de éxito o error.

### Principales Endpoints y Rutas

#### Autenticación y Gestión de Usuarios

- `GET /logout`: Cierra la sesión del usuario  
- `POST /api/registro`: Registro de nuevos usuarios  
- `POST /api/newdoc`: Registro de nuevos médicos  
- `POST /api/login`: Inicio de sesión de usuarios  
- `GET /perfil`: Visualización de perfil de usuario  

#### Gestión de Citas

- `POST /api/reserva`: Reserva de nuevas citas médicas  
- `POST /procesar_cita`: Procesa solicitudes de modificación o cancelación  
- `POST /cancel`: Cancelación de citas  
- `POST /modification`: Modificación de citas  
- `GET /citas`: Consulta de citas del usuario  

#### Procesamiento de Pagos

- `GET /pago`: Renderiza la interfaz para ingresar datos de pago  
- `POST /api/pago`: Procesa el pago de una cita (en desarrollo)  

---

## Flujos de Trabajo Principales

### Registro de Usuarios

1. Acceso a la página de registro (`newuser.html`)
2. Completar formulario
3. Validación y envío por AJAX
4. Registro en base de datos mediante procedimiento almacenado
5. Respuesta de éxito o error

### Inicio de Sesión

1. Acceso a la página de login (`login.html`)
2. Envío de credenciales
3. Validación y creación de sesión
4. Redirección según rol

### Reserva de Citas

1. Navegar a la página de reserva (`reservation.html`)
2. Llenar datos médicos y de contacto
3. Envío por POST a `/api/reserva`
4. Validación de datos y disponibilidad
5. Llamada a procedimiento almacenado `insertar_cita`
6. Respuesta:
   - `201`: Reserva exitosa
   - `400/500`: Error en la operación

### Modificación y Cancelación de Citas

1. Usuario ingresa folio de cita en `cancelacion.html` o `modificacion.html`
2. El sistema llama a `/procesar_cita`
3. Verifica si la cita existe
4. Si existe:
   - Renderiza formulario de cancelación o modificación
   - Envía solicitud
   - Actualiza estado en BD y muestra confirmación

### Procesamiento de Pagos

1. Usuario accede a `/pago`
2. Llena datos personales y de cuenta
3. Selecciona método de pago
4. Confirma operación  
5. (Lógica de backend en desarrollo)

---

## Integración con la Base de Datos

Se utilizan **procedimientos almacenados** para mantener la lógica en el servidor:

- `registro_usuario`: Registra nuevos usuarios
- `insertar_cita`: Inserta nuevas citas médicas
- `cancelar_cita`: Marca una cita como cancelada
- `modificar_cita`: Actualiza datos de una cita

---

## Manejo de Errores

### Backend

- Validación de entradas
- Manejo de fallas en conexión a BD
- Respuestas HTTP apropiadas (`200`, `400`, `401`, `404`, `500`, etc.)
- Mensajes descriptivos en JSON

### Frontend

- Validación de formularios
- Manejo de respuestas del servidor
- Alertas visuales para informar al usuario

---

## Seguridad

- Autenticación mediante sesiones
- Validación del lado del servidor
- Protección de rutas sensibles
- Hashing de contraseñas (en desarrollo)
- Control de acceso por roles

---

## Diagrama de Arquitectura

```text
+--------------------+
|     Frontend       |
|--------------------|
| HTML / CSS / JS    |
| Plantillas (Jinja) |
+---------+----------+
          |
          v
+--------------------+
|      Backend       |
|--------------------|
| Flask + Rutas      |
| Controladores      |
| Conexión a BD      |
+---------+----------+
          |
          v
+--------------------+
|    Base de Datos   |
|--------------------|
| MySQL              |
| Tablas             |
| Procedimientos SP  |
+--------------------+
```

---

