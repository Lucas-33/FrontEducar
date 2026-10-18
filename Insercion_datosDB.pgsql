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
-- Excepción: el usuario 'admin2' usa la contraseña 'admin1234'.
INSERT INTO usuario (username, password_hash, id_rol, legajo_alumno, legajo_profesor, id_padre, activo) VALUES 
('admin_gral', '$2b$12$ZmnciLXJxYuDt35EFBu5AeSRM/U09o7sGJgPfgt71lkxjeHkiHRvS', 1, NULL, NULL, NULL, TRUE),
('admin2', '$2b$12$w.Ew9VtyymFw1YcSTkzAu.Jg/HD7kV7bDJoOvxPbCavAZoF673HxK', 1, NULL, NULL, NULL, TRUE),

('lgomez', '$2b$12$ZmnciLXJxYuDt35EFBu5AeSRM/U09o7sGJgPfgt71lkxjeHkiHRvS', 2, NULL, 2001, NULL, TRUE),
('cruiz', '$2b$12$ZmnciLXJxYuDt35EFBu5AeSRM/U09o7sGJgPfgt71lkxjeHkiHRvS', 2, NULL, 2002, NULL, TRUE),

('rmartinez', '$2b$12$ZmnciLXJxYuDt35EFBu5AeSRM/U09o7sGJgPfgt71lkxjeHkiHRvS', 3, NULL, NULL, 1, TRUE),
('aperez', '$2b$12$ZmnciLXJxYuDt35EFBu5AeSRM/U09o7sGJgPfgt71lkxjeHkiHRvS', 3, NULL, NULL, 2, TRUE),

('tmartinez', '$2b$12$ZmnciLXJxYuDt35EFBu5AeSRM/U09o7sGJgPfgt71lkxjeHkiHRvS', 4, 1002, NULL, NULL, TRUE),
('mperez', '$2b$12$ZmnciLXJxYuDt35EFBu5AeSRM/U09o7sGJgPfgt71lkxjeHkiHRvS', 4, 1003, NULL, NULL, TRUE)
ON CONFLICT (username) DO NOTHING;

-- ==============================================================================
-- 5b. COMUNIDAD (formularios públicos y moderación)
-- ==============================================================================

INSERT INTO solicitud_inscripcion (postulante, dni, fecha_nacimiento, nivel, tutor, telefono, correo, fecha, estado, observaciones) VALUES 
('Julieta Acosta', '55123456', '2021-11-03', 'Inicial (Sala de 5)', 'Marina Acosta', '3624000001', 'marina.acosta@gmail.com', CURRENT_DATE - 6, 'Pendiente', NULL),
('Benjamín Romero', '53888999', '2018-07-14', 'Primario (2° Grado)', 'Diego Romero', '3624000002', 'diego.romero@hotmail.com', CURRENT_DATE - 20, 'Aprobado', 'Documentación completa. Entrevista realizada.'),
('Agustina Vega', '56777000', '2016-03-27', 'Primario (5° Grado)', 'Paola Vega', '3624000003', 'paola.vega@gmail.com', CURRENT_DATE - 12, 'Rechazado', 'Sin vacantes en el curso solicitado.');

INSERT INTO mensaje_contacto (nombre, telefono, correo, mensaje, fecha, leido) VALUES 
('Marcela Fernández', '3624112233', 'marcela.fdez@gmail.com', 'Buenas tardes, quisiera consultar por las vacantes disponibles en Sala de 4 para el ciclo 2027.', CURRENT_TIMESTAMP - INTERVAL '2 days', TRUE),
('Hugo Benítez', '3624223344', 'hugo.benitez@yahoo.com', '¿Cuáles son los horarios de atención de secretaría? Gracias.', CURRENT_TIMESTAMP - INTERVAL '5 hours', FALSE);

INSERT INTO opinion (nombre, vinculo, comentario, estrellas, fecha, aprobada) VALUES 
('Carla Duarte', 'Madre de 2° Grado', 'La atención de las maestras y el gabinete psicopedagógico es excelente. Mis hijos van felices a la escuela.', 5, CURRENT_DATE - 30, TRUE),
('Sergio Ramírez', 'Ex alumno promoción 2019', 'El nivel académico y los valores que me dejó el colegio fueron fundamentales para mi carrera universitaria.', 5, CURRENT_DATE - 15, TRUE),
('Lucía Torres', 'Vecina del barrio', 'Participé del taller de huerta comunitaria y me encantó la propuesta. Felicitaciones a los docentes por la organización.', 4, CURRENT_DATE - 3, FALSE);

INSERT INTO postulacion_empleo (nombre, correo, telefono, puesto, area, mensaje, fecha) VALUES 
('Verónica Ibarra', 'veronica.ibarra@gmail.com', '3624334455', 'Enfermero/a Profesional Matriculado/a', 'Gabinete de Salud y Enfermería', 'Cuento con matrícula provincial vigente y 8 años de experiencia en pediatría.', CURRENT_TIMESTAMP - INTERVAL '3 days'),
('Martín Correa', 'martin.correa@outlook.com', '3624445566', 'Postulación espontánea', 'Educación Física y Deportes', 'Soy profesor de educación física con experiencia en escuelas deportivas infantiles.', CURRENT_TIMESTAMP - INTERVAL '1 day');

-- ==============================================================================
-- 5c. EVALUACIÓN (calificaciones y asistencia)
-- ==============================================================================

-- Calificaciones coherentes con las asignaciones materia_curso_profesor del punto 3
INSERT INTO calificacion (legajo_alumno, id_materia, id_curso, periodo, tipo, nota, fecha, observacion, legajo_profesor) VALUES 
(1002, 1, 4, '1° Trimestre', 'Parcial', 8.50, CURRENT_DATE - 45, 'Buen desempeño en resolución de problemas.', 2001),
(1002, 1, 4, '1° Trimestre', 'Trabajo Práctico', 9.00, CURRENT_DATE - 20, NULL, 2001),
(1002, 6, 4, '1° Trimestre', 'Conceptual', 9.50, CURRENT_DATE - 15, 'Excelente participación en las clases.', 2002),
(1003, 1, 5, '1° Trimestre', 'Parcial', 7.25, CURRENT_DATE - 40, 'Debe reforzar operaciones con fracciones.', 2001),
(1003, 1, 5, '1° Trimestre', 'Trabajo Práctico', 8.00, CURRENT_DATE - 12, NULL, 2001),
(1003, 3, 5, '1° Trimestre', 'Oral', 8.75, CURRENT_DATE - 25, 'Muy buena exposición sobre la Revolución de Mayo.', 2004),
(1003, 5, 5, '1° Trimestre', 'Parcial', 6.50, CURRENT_DATE - 18, NULL, 2003),
(1004, 6, 6, '1° Trimestre', 'Conceptual', 10.00, CURRENT_DATE - 10, 'Líder positivo del grupo.', 2002);

-- Asistencia de los últimos días (un registro por alumno y fecha)
INSERT INTO asistencia (legajo_alumno, id_curso, fecha, estado, observacion, legajo_profesor) VALUES 
(1002, 4, CURRENT_DATE - 3, 'PRESENTE', NULL, 2001),
(1002, 4, CURRENT_DATE - 2, 'PRESENTE', NULL, 2001),
(1002, 4, CURRENT_DATE - 1, 'TARDE', 'Ingresó 15 minutos tarde por turno médico.', 2001),
(1003, 5, CURRENT_DATE - 3, 'PRESENTE', NULL, 2001),
(1003, 5, CURRENT_DATE - 2, 'AUSENTE', 'Ausencia sin aviso.', 2001),
(1003, 5, CURRENT_DATE - 1, 'JUSTIFICADO', 'Certificado médico presentado por la familia.', 2001),
(1004, 6, CURRENT_DATE - 2, 'PRESENTE', NULL, 2002),
(1004, 6, CURRENT_DATE - 1, 'PRESENTE', NULL, 2002)
ON CONFLICT (legajo_alumno, fecha) DO NOTHING;

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
SELECT setval(pg_get_serial_sequence('solicitud_inscripcion', 'id_solicitud'), COALESCE(MAX(id_solicitud), 1)) FROM solicitud_inscripcion;
SELECT setval(pg_get_serial_sequence('mensaje_contacto', 'id_mensaje'), COALESCE(MAX(id_mensaje), 1)) FROM mensaje_contacto;
SELECT setval(pg_get_serial_sequence('opinion', 'id_opinion'), COALESCE(MAX(id_opinion), 1)) FROM opinion;
SELECT setval(pg_get_serial_sequence('postulacion_empleo', 'id_postulacion'), COALESCE(MAX(id_postulacion), 1)) FROM postulacion_empleo;
SELECT setval(pg_get_serial_sequence('calificacion', 'id_calificacion'), COALESCE(MAX(id_calificacion), 1)) FROM calificacion;
SELECT setval(pg_get_serial_sequence('asistencia', 'id_asistencia'), COALESCE(MAX(id_asistencia), 1)) FROM asistencia;

COMMIT;