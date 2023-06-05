from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class Receta(BaseModel):
    id: int
    name: str
    ingredients: list

lista_recetas = [Receta(id=1, name="Huevo frito", ingredients=["huevo","aceite","sal"])]

@router.get("/recetas/{id}")
async def recetas(id: int):
    return lista_recetas[id-1]