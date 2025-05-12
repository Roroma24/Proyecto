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

- Registro de usuarios (pacientes y médicos)
- Reserva, modificación y cancelación de citas médicas
- Procesamiento de pagos

## Tecnologías Utilizadas

- **Backend:** Flask (Python)  
- **Base de Datos:** MySQL  
- **Frontend:** HTML, CSS, JavaScript  
- **Comunicación Cliente-Servidor:** AJAX, JSON  

---

## Estructura del Backend

### Conexión a la Base de Datos

Se utiliza `mysql-connector-python` para manejar la conexión mediante la función `conectar_db()`, la cual proporciona mensajes de éxito o error.

### Rutas Principales

#### Autenticación y Gestión de Usuarios

- `GET /logout`: Cierra la sesión del usuario  
- `POST /api/registro`: Registro de nuevos usuarios  
- `POST /api/newdoc`: Registro de nuevos médicos  

#### Gestión de Citas

- `POST /api/reserva`: Reserva de nuevas citas médicas  
- `POST /procesar_cita`: Procesa solicitudes de modificación o cancelación  
- `POST /cancel`: Cancelación de citas  
- `POST /modification`: Modificación de citas  

#### Procesamiento de Pagos

- `GET /pago`: Renderiza la interfaz para ingresar datos de pago

---

## Flujos de Trabajo Principales

### Registro de Usuarios

1. Acceso a la página de registro (`newuser.html`)
2. Completar formulario
3. Validación y envío por AJAX
4. Registro en base de datos
5. Respuesta de éxito o error

### Reserva de Citas

1. Navegar a la página de reserva (`reservation.html`)
2. Llenar datos médicos y de contacto
3. Envío por POST a `/api/reserva`
4. Validación de datos
5. Llamada a procedimiento almacenado `insertar_cita`
6. Respuesta:
   - `201`: Reserva exitosa
   - `400/500`: Error en la operación

### Cancelación de Citas

1. Usuario ingresa folio de cita en `cancelacion.html`
2. El sistema llama a `/procesar_cita`
3. Verifica si la cita existe
4. Si existe:
   - Renderiza formulario de cancelación
   - Envía cancelación
   - (Faltan confirmaciones/actualización en BD)

### Procesamiento de Pagos

1. Usuario accede a `/pago`
2. Llena datos personales y de cuenta
3. Selecciona método de pago
4. Confirma operación  
*(Actualmente no hay lógica de procesamiento implementada)*

---

## Integración con la Base de Datos

Se utilizan **procedimientos almacenados** para mantener la lógica en el servidor:

- `registro_usuario`: Registra nuevos usuarios
- `insertar_cita`: Inserta nuevas citas médicas

---

## Manejo de Errores

### Backend

- Validación de entradas
- Manejo de fallas en conexión a BD
- Respuestas HTTP apropiadas (`200`, `400`, `500`, etc.)

### Frontend

- Validación de formularios
- Manejo de respuestas del servidor
- Alertas visuales para informar al usuario

---

## Seguridad

- Autenticación mediante sesiones
- Validación del lado del servidor
- Protección de rutas sensibles

---

## Limitaciones y Mejoras Futuras

### Cancelación de Citas

- Falta actualización en BD para marcar como "cancelada"
- Formulario sin manejador de envío
- No hay mensaje de confirmación

### Procesamiento de Pagos

- Lógica de backend no implementada
- Falta validación de pagos
- No hay integración con pasarelas externas
- Flujo de confirmación incompleto

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
