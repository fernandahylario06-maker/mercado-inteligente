from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .database import Base, engine
from . import models
from .routes.products import router as products_router
from .routes.movements import router as movements_router

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Mercado Inteligente", version="0.2.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
app.include_router(products_router)
app.include_router(movements_router)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request, name="home.html", context={"title": "Controle de estoque e validade"}
    )
