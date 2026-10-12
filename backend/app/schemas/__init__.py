from backend.app.schemas.seguridad import (
    RolBase, RolCreate, RolResponse,
    UsuarioBase, UsuarioCreate, UsuarioUpdate, UsuarioResponse,
    LoginRequest, Token, TokenData,
)
from backend.app.schemas.academico import (
    NivelEducativoBase, NivelEducativoCreate, NivelEducativoResponse,
    CursoBase, CursoCreate, CursoResponse,
    MateriaBase, MateriaCreate, MateriaResponse,
    MateriaCursoProfesorBase, MateriaCursoProfesorCreate, MateriaCursoProfesorResponse,
)
from backend.app.schemas.personas import (
    AlumnoBase, AlumnoCreate, AlumnoUpdate, AlumnoResponse,
    ProfesorBase, ProfesorCreate, ProfesorUpdate, ProfesorResponse,
    PadreBase, PadreCreate, PadreUpdate, PadreResponse,
    PadreAlumnoBase, PadreAlumnoCreate, PadreAlumnoResponse,
)
from backend.app.schemas.servicios import (
    HorarioBase, HorarioCreate, HorarioResponse,
    DeporteBase, DeporteCreate, DeporteResponse,
    GrupoDeporteBase, GrupoDeporteCreate, GrupoDeporteResponse,
    InscripcionDeporteCreate, InscripcionDeporteResponse,
    RecorridoTransporteBase, RecorridoTransporteCreate, RecorridoTransporteResponse,
    InscripcionTransporteCreate, InscripcionTransporteResponse,
    InscripcionComedorCreate, InscripcionComedorResponse,
)
