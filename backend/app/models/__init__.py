from backend.app.models.seguridad import Rol, Usuario
from backend.app.models.academico import NivelEducativo, Curso, Materia, MateriaCursoProfesor
from backend.app.models.personas import Alumno, Profesor, Padre, PadreAlumno
from backend.app.models.servicios import (
    Horario,
    Deporte,
    GrupoDeporte,
    InscripcionDeporte,
    RecorridoTransporte,
    InscripcionTransporte,
    InscripcionComedor,
)
from backend.app.models.comunidad import (
    MensajeContacto,
    Opinion,
    PostulacionEmpleo,
    SolicitudInscripcion,
)
from backend.app.models.evaluacion import Asistencia, Calificacion