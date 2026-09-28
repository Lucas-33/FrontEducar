from fastapi import APIRouter

router = APIRouter()

noticias_fake = [
    {"id": 1, "titulo": "Inicio de inscripciones 2027", "contenido": "Ya están abiertas..."},
    {"id": 2, "titulo": "Nueva pileta climatizada", "contenido": "Se inauguró..."},
]

@router.get("/")
def listar_noticias():
    return noticias_fake