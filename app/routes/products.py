
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Product


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/produtos")
def list_products(
    request: Request,
    db: Session = Depends(get_db),
):
    products = db.scalars(
        select(Product).order_by(Product.name)
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="products.html",
        context={
            "products": products,
            "error": request.query_params.get("erro"),
        },
    )


@router.post("/produtos")
def create_product(
    name: str = Form(...),
    category: str = Form(...),
    unit: str = Form("unidade"),
    db: Session = Depends(get_db),
):
    # Remove espaços desnecessários dos campos.
    name = name.strip()
    category = category.strip()
    unit = unit.strip() or "unidade"

    # Valida campos obrigatórios.
    if not name or not category:
        return RedirectResponse(
            url="/produtos?erro=campos",
            status_code=303,
        )

    # Valida os limites definidos nos modelos.
    if len(name) > 120 or len(category) > 80 or len(unit) > 20:
        return RedirectResponse(
            url="/produtos?erro=limite",
            status_code=303,
        )

    product = Product(
        name=name,
        category=category,
        unit=unit,
    )

    try:
        db.add(product)
        db.commit()

    except IntegrityError:
        db.rollback()
        return RedirectResponse(
            url="/produtos?erro=duplicado",
            status_code=303,
        )

    except SQLAlchemyError:
        db.rollback()
        return RedirectResponse(
            url="/produtos?erro=banco",
            status_code=303,
        )

    return RedirectResponse(
        url="/produtos",
        status_code=303,
    )
