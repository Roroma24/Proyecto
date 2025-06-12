CREATE DATABASE hospital;

USE hospital;

CREATE TABLE usuario (
  id_usuario INT AUTO_INCREMENT PRIMARY KEY, 
  nombre VARCHAR(200) NOT NULL,
  primer_apellido VARCHAR(200) NOT NULL,
  segundo_apellido VARCHAR(200),
  rol ENUM('Paciente', 'Doctor'),
  correo VARCHAR(50) NOT NULL UNIQUE,
  contraseña VARCHAR(256) NOT NULL
);

CREATE TABLE notificacion (
  id_notificacion INT AUTO_INCREMENT PRIMARY KEY,
  mensaje TEXT,
  fecha_de_envio DATETIME,
  id_usuario INT,
  FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
) AUTO_INCREMENT = 100;

CREATE TABLE doctor (
  id_doctor INT AUTO_INCREMENT PRIMARY KEY,
  telefono VARCHAR(20) NOT NULL,
  cedula_profesional VARCHAR(8) NOT NULL,
  curp VARCHAR(18) NOT NULL,
  rfc VARCHAR(13) NOT NULL,
  id_usuario INT NOT NULL,
  FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
) AUTO_INCREMENT = 2000;

CREATE TABLE especialidad (
  id_especialidad INT AUTO_INCREMENT PRIMARY KEY,
  nombre_especialidad VARCHAR(50) NOT NULL UNIQUE
) AUTO_INCREMENT = 200;

CREATE TABLE doctor_especialidad (
  id_doctor INT,
  id_especialidad INT,
  FOREIGN KEY (id_doctor) REFERENCES doctor(id_doctor),
  FOREIGN KEY (id_especialidad) REFERENCES especialidad(id_especialidad)
);

CREATE TABLE paciente (
  id_paciente INT AUTO_INCREMENT PRIMARY KEY,
  curp VARCHAR(18) NOT NULL,
  edad INT NOT NULL,
  telefono VARCHAR(20) NOT NULL,
  alergias VARCHAR(200),
  discapacidad VARCHAR(50),
  id_usuario INT NOT NULL,
  FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
) AUTO_INCREMENT = 6000;

CREATE TABLE clinica (
  id_clinica INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(200) NOT NULL,
  telefono VARCHAR(20) NOT NULL UNIQUE,
  rfc VARCHAR(12) NOT NULL
) AUTO_INCREMENT = 300;

CREATE TABLE sucursal (
  id_sucursal INT AUTO_INCREMENT PRIMARY KEY,
  direccion VARCHAR(200) NOT NULL UNIQUE,
  id_clinica INT NOT NULL,
  FOREIGN KEY (id_clinica) REFERENCES clinica(id_clinica)
);

CREATE TABLE cita (
  id_cita INT AUTO_INCREMENT PRIMARY KEY,
  fecha_cita DATE NOT NULL,
  horario TIME NOT NULL,
  id_paciente INT NOT NULL,
  id_sucursal INT NOT NULL,
  FOREIGN KEY (id_paciente) REFERENCES paciente(id_paciente),
  FOREIGN KEY (id_sucursal) REFERENCES sucursal(id_sucursal)
) AUTO_INCREMENT = 600;

CREATE TABLE pago (
  id_pago INT AUTO_INCREMENT PRIMARY KEY,
  tipo_de_pago ENUM('adelanto', 'pago total') NOT NULL,
  monto DECIMAL(10,2) NOT NULL,
  fecha_de_pago DATETIME NOT NULL,
  metodo_de_pago VARCHAR(100) NOT NULL,
  numero_cuenta VARCHAR(18) NOT NULL,
  id_cita INT NOT NULL,
  FOREIGN KEY (id_cita) REFERENCES cita(id_cita)
) AUTO_INCREMENT = 700;

CREATE TABLE historial_medico (
  id_historial INT AUTO_INCREMENT PRIMARY KEY,
  detalle TEXT,
  fecha DATE,
  id_paciente INT,
  FOREIGN KEY (id_paciente) REFERENCES paciente(id_paciente)
) AUTO_INCREMENT = 800;

DELIMITER $$

CREATE PROCEDURE registro_usuario(
  IN nombre VARCHAR(200),
  IN apellido1 VARCHAR(200),
  IN apellido2 VARCHAR(200),
  IN correo VARCHAR(50),
  IN password VARCHAR(20),
  OUT new_id_usuario INT 
)
BEGIN
  INSERT INTO usuario (nombre, primer_apellido, segundo_apellido, correo, contraseña, rol)
  VALUES (nombre, apellido1, apellido2, correo, SHA2(password, 256), 'Paciente');
  
  SET new_id_usuario = LAST_INSERT_ID();
END$$

CREATE PROCEDURE registro_doctor (
  IN p_nombre VARCHAR(200),
  IN p_apellido1 VARCHAR(200),
  IN p_apellido2 VARCHAR(200),
  IN p_correo VARCHAR(50),
  IN p_contraseña VARCHAR(20),
  IN p_telefono VARCHAR(20),
  IN p_cedula VARCHAR(8),
  IN p_curp VARCHAR(18),
  IN p_rfc VARCHAR(13),
  IN p_especialidad VARCHAR(50),
  OUT new_id INT
)
BEGIN
  DECLARE especialidad_id INT;
  DECLARE id_usuario INT;
  DECLARE id_doctor INT;

  INSERT INTO usuario (nombre, primer_apellido, segundo_apellido, rol, correo, contraseña)
  VALUES (p_nombre, p_apellido1, p_apellido2, 'Doctor', p_correo, SHA2(p_contraseña, 256));

  SET id_usuario = LAST_INSERT_ID();

  INSERT INTO doctor (telefono, cedula_profesional, curp, rfc, id_usuario)
  VALUES (p_telefono, p_cedula, p_curp, p_rfc, id_usuario);

  SET id_doctor = LAST_INSERT_ID();

  SELECT id_especialidad INTO especialidad_id
  FROM especialidad
  WHERE nombre_especialidad = p_especialidad
  LIMIT 1;

  IF especialidad_id IS NULL THEN
    INSERT INTO especialidad(nombre_especialidad)
    VALUES (p_especialidad);
    SET especialidad_id = LAST_INSERT_ID();
  END IF;

  INSERT INTO doctor_especialidad(id_doctor, id_especialidad)
  VALUES (id_doctor, especialidad_id);

  SET new_id = id_doctor;
END$$

CREATE PROCEDURE insertar_cita(
  IN p_id_usuario INT,
  IN p_curp VARCHAR(18),
  IN p_edad INT,
  IN p_telefono VARCHAR(15),
  IN p_alergias VARCHAR(50),
  IN p_discapacidad VARCHAR(50),
  IN p_fecha DATE,
  IN p_horario TIME,
  IN p_direccion VARCHAR(200),
  IN nombre_especialidad VARCHAR(50)
)
BEGIN
  DECLARE existing_id_paciente INT;
  DECLARE new_id_cita INT;
  DECLARE id_clinica_existente INT;
  DECLARE id_sucursal_existente INT;

  SELECT id_paciente INTO existing_id_paciente
  FROM paciente
  WHERE curp = p_curp
  LIMIT 1;

  IF existing_id_paciente IS NULL THEN
    INSERT INTO paciente (curp, edad, telefono, alergias, discapacidad, id_usuario)
    VALUES (p_curp, p_edad, p_telefono, p_alergias, p_discapacidad, p_id_usuario);

    SET existing_id_paciente = LAST_INSERT_ID();
  ELSE
    UPDATE paciente
    SET edad = IF(edad != p_edad, p_edad, edad),
        telefono = IF(telefono != p_telefono, p_telefono, telefono),
        alergias = IF(alergias != p_alergias, p_alergias, alergias),
        discapacidad = IF(discapacidad != p_discapacidad, p_discapacidad, discapacidad)
    WHERE id_paciente = existing_id_paciente;
  END IF;

  SELECT id_clinica INTO id_clinica_existente
  FROM clinica
  WHERE nombre = "Hospital_Qualitas"
  LIMIT 1;

  IF id_clinica_existente IS NULL THEN
    INSERT INTO clinica (nombre, telefono, rfc)
    VALUES ("Hospital_Qualitas", "5596826800", "sjsdHj245s98");
    SET id_clinica_existente = LAST_INSERT_ID();
  END IF;

  SELECT id_sucursal INTO id_sucursal_existente
  FROM sucursal
  WHERE direccion = p_direccion
  LIMIT 1;

  IF id_sucursal_existente IS NULL THEN
    INSERT INTO sucursal (direccion, id_clinica)
    VALUES (p_direccion, id_clinica_existente);
    SET id_sucursal_existente = LAST_INSERT_ID();
  END IF;

  INSERT INTO cita (id_paciente, fecha_cita, horario, id_sucursal)
  VALUES (existing_id_paciente, p_fecha, p_horario, id_sucursal_existente);

  IF NOT EXISTS (
    SELECT 1 FROM especialidad WHERE nombre_especialidad = nombre_especialidad
  ) THEN
    INSERT INTO especialidad (nombre_especialidad)
    VALUES (nombre_especialidad);
  END IF;
END$$

CREATE PROCEDURE modificar_cita(
  IN p_id_cita INT,
  IN p_fecha_cita DATE,
  IN p_horario TIME,
  IN p_telefono_paciente VARCHAR(20),
  IN p_alergias VARCHAR(200),
  IN p_direccion_clinica VARCHAR(200),
  IN p_especialidad VARCHAR(50),
  IN p_discapacidad VARCHAR(50)
)
BEGIN
  DECLARE v_id_paciente INT;
  DECLARE v_id_clinica INT;
  DECLARE v_id_sucursal INT;
  DECLARE v_id_especialidad INT;

  UPDATE cita
  SET fecha_cita = p_fecha_cita,
      horario = p_horario
  WHERE id_cita = p_id_cita;

  SELECT id_paciente INTO v_id_paciente
  FROM cita
  WHERE id_cita = p_id_cita;

  UPDATE paciente
  SET telefono = p_telefono_paciente,
      alergias = p_alergias,
      discapacidad = p_discapacidad 
  WHERE id_paciente = v_id_paciente;

  SELECT id_clinica INTO v_id_clinica
  FROM clinica
  WHERE nombre = "Hospital_Qualitas"
  LIMIT 1;

  SELECT id_sucursal INTO v_id_sucursal
  FROM sucursal
  WHERE direccion = p_direccion_clinica
  LIMIT 1;

  IF v_id_sucursal IS NULL THEN
    INSERT INTO sucursal (direccion, id_clinica)
    VALUES (p_direccion_clinica, v_id_clinica);
    SET v_id_sucursal = LAST_INSERT_ID();
  END IF;

  UPDATE cita
  SET id_sucursal = v_id_sucursal
  WHERE id_cita = p_id_cita;

  SELECT id_especialidad INTO v_id_especialidad
  FROM especialidad
  WHERE nombre_especialidad = p_especialidad
  LIMIT 1;

  IF v_id_especialidad IS NULL THEN
    INSERT INTO especialidad(nombre_especialidad)
    VALUES (p_especialidad);
  END IF;
END$$

CREATE PROCEDURE eliminar_cita(
  IN p_id_cita INT
)
BEGIN
  DECLARE v_id_paciente INT;

  SELECT id_paciente INTO v_id_paciente
  FROM cita
  WHERE id_cita = p_id_cita;

  DELETE FROM pago WHERE id_cita = p_id_cita;
  DELETE FROM cita WHERE id_cita = p_id_cita;

  IF NOT EXISTS (
    SELECT 1 FROM cita WHERE id_paciente = v_id_paciente
  ) THEN
    DELETE FROM paciente WHERE id_paciente = v_id_paciente;
  END IF;
END$$

CREATE PROCEDURE registrar_pago(
  IN p_tipo_de_pago ENUM('adelanto', 'pago total'),
  IN p_monto DECIMAL(10,2),
  IN p_metodo_de_pago VARCHAR(100),
  IN p_numero_cuenta VARCHAR(16),
  IN p_id_cita INT
)
BEGIN
  INSERT INTO pago (tipo_de_pago, monto, fecha_de_pago, metodo_de_pago, numero_cuenta, id_cita)
  VALUES (p_tipo_de_pago, p_monto, NOW(), p_metodo_de_pago, p_numero_cuenta, p_id_cita);
END$$

DELIMITER ;