-- ==============================================================================
-- SCRIPT DE INSERCIÓN DE DATOS (SEED DATA) - educar_db
-- ==============================================================================

BEGIN;

-- ==============================================================================
-- 1. TABLAS MAESTRAS Y CATÁLOGOS (Sin dependencias)
-- ==============================================================================

INSERT INTO rol (id_rol, nombre) VALUES 
(1, 'ADMIN'), 
(2, 'TEACHER'), 
(3, 'PARENT'), 
(4, 'STUDENT')
ON CONFLICT (id_rol) DO NOTHING;

INSERT INTO nivel_educativo (id_nivel, nombre) VALUES 
(1, 'Inicial'), 
(2, 'Primario'), 
(3, 'Secundario')
ON CONFLICT (id_nivel) DO NOTHING;

INSERT INTO horario (id_horario, descripcion) VALUES 
(1, 'Turno Mañana (08:00 - 12:00)'),
(2, 'Turno Tarde (13:00 - 17:00)'),
(3, 'Vespertino / Extracurricular (17:30 - 19:30)')
ON CONFLICT (id_horario) DO NOTHING;

INSERT INTO recorrido_transporte (id_recorrido, descripcion) VALUES 
(1, 'Ruta Centro - Norte'),
(2, 'Ruta Sur - Barranqueras')
ON CONFLICT (id_recorrido) DO NOTHING;

INSERT INTO materia (id_materia, nombre) VALUES 
(1, 'Matemática'), 
(2, 'Prácticas del Lenguaje'), 
(3, 'Historia Argentina'),
(4, 'Biología'), 
(5, 'Inglés'), 
(6, 'Educación Física')
ON CONFLICT (id_materia) DO NOTHING;

-- ==============================================================================
-- 2. ENTIDADES DEPENDIENTES DE PRIMER NIVEL
-- ==============================================================================

INSERT INTO curso (id_curso, nombre, id_nivel) VALUES 
(1, 'Sala de 4', 1),
(2, 'Sala de 5', 1),
(3, '1° Grado A', 2),
(4, '6° Grado B', 2),
(5, '1° Año A', 3),
(6, '5° Año B', 3)
ON CONFLICT (id_curso) DO NOTHING;

INSERT INTO profesor (legajo, dni, nombre, apellido, especialidad, correo_electronico, telefono, estado) VALUES 
(2001, '30123456', 'Laura', 'Gómez', 'Matemática y Física', 'laura.gomez@educar.edu.ar', '3624111111', 'ACTIVO'),
(2002, '31234567', 'Carlos', 'Ruiz', 'Educación Física', 'carlos.ruiz@educar.edu.ar', '3624222222', 'ACTIVO'),
(2003, '28987654', 'Mariana', 'López', 'Idiomas', 'mariana.lopez@educar.edu.ar', '3624333333', 'ACTIVO'),
(2004, '34567890', 'Javier', 'Fernández', 'Ciencias Sociales', 'javier.fernandez@educar.edu.ar', '3624444444', 'ACTIVO')
ON CONFLICT (legajo) DO NOTHING;

INSERT INTO deporte (id_deporte, nombre, legajo_profesor_responsable) VALUES 
(1, 'Fútbol', 2002),
(2, 'Vóleibol', 2002),
(3, 'Básquetbol', 2002)
ON CONFLICT (id_deporte) DO NOTHING;

INSERT INTO padre (id_padre, dni, nombre, apellido, telefono, correo_electronico) VALUES 
(1, '20111222', 'Roberto', 'Martínez', '3624555555', 'roberto.martinez@gmail.com'),
(2, '22333444', 'Ana', 'Pérez', '3624666666', 'ana.perez@hotmail.com'),
(3, '24555666', 'Martín', 'Sánchez', '3624777777', 'martin.sanchez@yahoo.com'),
(4, '26777888', 'Lucía', 'García', '3624888888', 'lucia.garcia@gmail.com')
ON CONFLICT (id_padre) DO NOTHING;

-- ==============================================================================
-- 3. ENTIDADES PRINCIPALES (Múltiples dependencias)
-- ==============================================================================

-- Fechas de nacimiento acordes a los niveles escolares esperados en Argentina
INSERT INTO alumno (legajo, dni, nombre, apellido, fecha_nacimiento, domicilio, telefono, correo_electronico, id_curso, estado_alumno) VALUES 
(1001, '58111222', 'Sofía', 'Martínez', '2022-05-10', 'Av. Alberdi 123, Resistencia', '3624555555', NULL, 1, 'ACTIVO'), -- Sala de 4
(1002, '54111222', 'Tomás', 'Martínez', '2015-08-20', 'Av. Alberdi 123, Resistencia', '3624555555', 'tomas.martinez@alumno.educar.ar', 4, 'ACTIVO'), -- 6° Grado
(1003, '52333444', 'Mateo', 'Pérez', '2013-02-15', 'Calle French 456, Resistencia', '3624666666', 'mateo.perez@alumno.educar.ar', 5, 'ACTIVO'), -- 1° Año
(1004, '48555666', 'Valentina', 'Sánchez', '2009-11-30', 'Av. San Martín 789, Resistencia', '3624777777', 'valentina.sanchez@alumno.educar.ar', 6, 'ACTIVO'), -- 5° Año
(1005, '56777888', 'Lucas', 'García', '2020-04-12', 'Arturo Illia 101, Resistencia', '3624888888', NULL, 3, 'ACTIVO'), -- 1° Grado
(1006, '57888999', 'Camila', 'García', '2021-09-05', 'Arturo Illia 101, Resistencia', '3624888888', NULL, 2, 'ACTIVO') -- Sala de 5
ON CONFLICT (legajo) DO NOTHING;

INSERT INTO grupo_deporte (id_grupo, id_deporte, id_nivel, id_horario) VALUES 
(1, 1, 2, 3), -- Fútbol, Nivel Primario, Vespertino
(2, 2, 3, 3), -- Vóleibol, Nivel Secundario, Vespertino
(3, 3, 3, 3)  -- Básquetbol, Nivel Secundario, Vespertino
ON CONFLICT (id_grupo) DO NOTHING;

INSERT INTO materia_curso_profesor (id_materia, id_curso, legajo_profesor) VALUES 
(1, 4, 2001), -- Matemática 6° Grado (Laura)
(1, 5, 2001), -- Matemática 1° Año (Laura)
(3, 5, 2004), -- Historia 1° Año (Javier)
(5, 5, 2003), -- Inglés 1° Año (Mariana)
(6, 4, 2002), -- Ed. Física 6° Grado (Carlos)
(6, 6, 2002)  -- Ed. Física 5° Año (Carlos)
ON CONFLICT (id_materia, id_curso) DO NOTHING;

-- ==============================================================================
-- 4. RELACIONES INTERMEDIAS E INSCRIPCIONES
-- ==============================================================================

INSERT INTO padre_alumno (id_padre, legajo_alumno) VALUES 
(1, 1001), -- Roberto es padre de Sofía
(1, 1002), -- Roberto es padre de Tomás (Hermanos)
(2, 1003), -- Ana es madre de Mateo
(3, 1004), -- Martín es padre de Valentina
(4, 1005), -- Lucía es madre de Lucas
(4, 1006)  -- Lucía es madre de Camila (Hermanos)
ON CONFLICT (id_padre, legajo_alumno) DO NOTHING;

INSERT INTO inscripcion_deporte (legajo_alumno, id_grupo, fecha_inscripcion) VALUES 
(1002, 1, CURRENT_DATE), -- Tomás en Fútbol Primario
(1003, 2, CURRENT_DATE), -- Mateo en Vóleibol Secundario
(1004, 3, CURRENT_DATE)  -- Valentina en Básquetbol Secundario
ON CONFLICT (legajo_alumno, id_grupo) DO NOTHING;

INSERT INTO inscripcion_transporte (legajo_alumno, id_recorrido, fecha_alta, estado) VALUES 
(1001, 1, CURRENT_DATE, 'ACTIVO'),
(1002, 1, CURRENT_DATE, 'ACTIVO'),
(1005, 2, CURRENT_DATE, 'ACTIVO')
ON CONFLICT (legajo_alumno) DO NOTHING;

INSERT INTO inscripcion_comedor (legajo_alumno, fecha_alta, estado) VALUES 
(1003, CURRENT_DATE, 'ACTIVO'),
(1004, CURRENT_DATE, 'ACTIVO')
ON CONFLICT (legajo_alumno) DO NOTHING;

-- ==============================================================================
-- 5. SEGURIDAD Y ACCESOS (RBAC)
-- ==============================================================================

-- La contraseña para todos es 'password123' procesada con bcrypt.
INSERT INTO usuario (username, password_hash, id_rol, legajo_alumno, legajo_profesor, id_padre, activo) VALUES 
('admin_gral', '$2b$12$ZmnciLXJxYuDt35EFBu5AeSRM/U09o7sGJgPfgt71lkxjeHkiHRvS', 1, NULL, NULL, NULL, TRUE),

('lgomez', '$2b$12$ZmnciLXJxYuDt35EFBu5AeSRM/U09o7sGJgPfgt71lkxjeHkiHRvS', 2, NULL, 2001, NULL, TRUE),
('cruiz', '$2b$12$ZmnciLXJxYuDt35EFBu5AeSRM/U09o7sGJgPfgt71lkxjeHkiHRvS', 2, NULL, 2002, NULL, TRUE),

('rmartinez', '$2b$12$ZmnciLXJxYuDt35EFBu5AeSRM/U09o7sGJgPfgt71lkxjeHkiHRvS', 3, NULL, NULL, 1, TRUE),
('aperez', '$2b$12$ZmnciLXJxYuDt35EFBu5AeSRM/U09o7sGJgPfgt71lkxjeHkiHRvS', 3, NULL, NULL, 2, TRUE),

('tmartinez', '$2b$12$ZmnciLXJxYuDt35EFBu5AeSRM/U09o7sGJgPfgt71lkxjeHkiHRvS', 4, 1002, NULL, NULL, TRUE),
('mperez', '$2b$12$ZmnciLXJxYuDt35EFBu5AeSRM/U09o7sGJgPfgt71lkxjeHkiHRvS', 4, 1003, NULL, NULL, TRUE)
ON CONFLICT (username) DO NOTHING;

-- ==============================================================================
-- 6. ACTUALIZACIÓN DE SECUENCIAS IDENTITY (PREVENCIÓN DE ERRORES)
-- ==============================================================================

-- Al insertar IDs explícitos, las secuencias internas de PG quedan desfasadas.
-- Estas funciones ajustan automáticamente el contador interno al valor máximo insertado.
SELECT setval(pg_get_serial_sequence('rol', 'id_rol'), COALESCE(MAX(id_rol), 1)) FROM rol;
SELECT setval(pg_get_serial_sequence('nivel_educativo', 'id_nivel'), COALESCE(MAX(id_nivel), 1)) FROM nivel_educativo;
SELECT setval(pg_get_serial_sequence('horario', 'id_horario'), COALESCE(MAX(id_horario), 1)) FROM horario;
SELECT setval(pg_get_serial_sequence('recorrido_transporte', 'id_recorrido'), COALESCE(MAX(id_recorrido), 1)) FROM recorrido_transporte;
SELECT setval(pg_get_serial_sequence('materia', 'id_materia'), COALESCE(MAX(id_materia), 1)) FROM materia;
SELECT setval(pg_get_serial_sequence('curso', 'id_curso'), COALESCE(MAX(id_curso), 1)) FROM curso;
SELECT setval(pg_get_serial_sequence('padre', 'id_padre'), COALESCE(MAX(id_padre), 1)) FROM padre;
SELECT setval(pg_get_serial_sequence('deporte', 'id_deporte'), COALESCE(MAX(id_deporte), 1)) FROM deporte;
SELECT setval(pg_get_serial_sequence('grupo_deporte', 'id_grupo'), COALESCE(MAX(id_grupo), 1)) FROM grupo_deporte;

COMMIT;