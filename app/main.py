from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from fastapi import Depends
from .database import Base, engine, get_db
from . import models
from .routes.products import router as products_router
from .routes.movements import router as movements_router
from .routes.alerts import router as alerts_router
from .models import Product, Batch

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Mercado Inteligente", version="1.0.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
app.include_router(products_router)
app.include_router(movements_router)
app.include_router(alerts_router)


@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    product_count = db.scalar(select(func.count(Product.id))) or 0
    batch_count = db.scalar(select(func.count(Batch.id))) or 0
    stock_total = db.scalar(select(func.coalesce(func.sum(Batch.quantity), 0))) or 0
    return templates.TemplateResponse(
        request=request, name="home.html",
        context={"product_count": product_count, "batch_count": batch_count, "stock_total": stock_total}
    )
