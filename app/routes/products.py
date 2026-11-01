from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Product

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/produtos")
def list_products(request: Request, db: Session = Depends(get_db)):
    products = db.scalars(select(Product).order_by(Product.name)).all()
    return templates.TemplateResponse(
        request=request, name="products.html", context={"products": products, "error": None}
    )


@router.post("/produtos")
def create_product(
    name: str = Form(...),
    category: str = Form(...),
    unit: str = Form("unidade"),
    db: Session = Depends(get_db),
):
    product = Product(name=name.strip(), category=category.strip(), unit=unit.strip())
    db.add(product)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return RedirectResponse(url="/produtos?erro=duplicado", status_code=303)
    return RedirectResponse(url="/produtos", status_code=303)
