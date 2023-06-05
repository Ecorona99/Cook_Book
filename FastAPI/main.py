from fastapi import FastAPI
from routers import recetas

app = FastAPI()

app.include_router(recetas.router)

@app.get("/")
async def root():
    return "Server Created"
