from backend.app.repositories.academico import (
    curso_repository,
    materia_curso_profesor_repository,
    materia_repository,
    nivel_repository,
)
from backend.app.repositories.base import CRUDBase
from backend.app.repositories.comunidad import (
    mensaje_contacto_repository,
    opinion_repository,
    postulacion_empleo_repository,
    solicitud_inscripcion_repository,
)
from backend.app.repositories.evaluacion import (
    asistencia_repository,
    calificacion_repository,
)
from backend.app.repositories.personas import (
    alumno_repository,
    padre_alumno_repository,
    padre_repository,
    profesor_repository,
)
from backend.app.repositories.seguridad import rol_repository, usuario_repository
from backend.app.repositories.servicios import (
    deporte_repository,
    grupo_deporte_repository,
    horario_repository,
    inscripcion_comedor_repository,
    inscripcion_deporte_repository,
    inscripcion_transporte_repository,
    recorrido_transporte_repository,
)
