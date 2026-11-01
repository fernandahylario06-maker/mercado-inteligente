
from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import models
from .database import Base, engine, get_db
from .models import Batch, Product
from .routes.alerts import router as alerts_router
from .routes.movements import router as movements_router
from .routes.products import router as products_router


# Cria as tabelas que ainda não existem no banco.
# Observação: create_all não altera tabelas existentes.
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Mercado Inteligente",
    version="1.0.0",
)


# Configuração dos arquivos estáticos e templates.
app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

templates = Jinja2Templates(directory="app/templates")


# Registro das rotas da aplicação.
app.include_router(products_router)
app.include_router(movements_router)
app.include_router(alerts_router)


@app.get("/")
def home(
    request: Request,
    db: Session = Depends(get_db),
):
    # Calcula os indicadores do painel.
    product_count = db.scalar(
        select(func.count(Product.id))
    ) or 0

    batch_count = db.scalar(
        select(func.count(Batch.id))
    ) or 0

    stock_total = db.scalar(
        select(func.coalesce(func.sum(Batch.quantity), 0))
    ) or 0

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "product_count": product_count,
            "batch_count": batch_count,
            "stock_total": stock_total,
        },
    )
