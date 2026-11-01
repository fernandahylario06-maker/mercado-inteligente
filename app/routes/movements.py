from datetime import date
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import Batch, Movement, Product

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/movimentacoes")
def list_movements(request: Request, db: Session = Depends(get_db)):
    products = db.scalars(select(Product).order_by(Product.name)).all()
    batches = db.scalars(select(Batch).options(joinedload(Batch.product)).order_by(Batch.expires_at)).all()
    movements = db.scalars(
        select(Movement).options(joinedload(Movement.product), joinedload(Movement.batch))
        .order_by(Movement.occurred_at.desc())
    ).all()
    return templates.TemplateResponse(
        request=request, name="movements.html",
        context={"products": products, "batches": batches, "movements": movements, "error": request.query_params.get("erro")}
    )


@router.post("/movimentacoes")
def create_movement(
    batch_id: int = Form(...),
    movement_type: str = Form(...),
    quantity: int = Form(...),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    batch = db.get(Batch, batch_id)
    if batch is None or quantity <= 0 or movement_type not in {"entrada", "saida"}:
        return RedirectResponse(url="/movimentacoes?erro=dados", status_code=303)
    if movement_type == "saida" and quantity > batch.quantity:
        return RedirectResponse(url="/movimentacoes?erro=saldo", status_code=303)
    if movement_type == "entrada":
        batch.quantity += quantity
    else:
        batch.quantity -= quantity
    db.add(Movement(
        product_id=batch.product_id, batch_id=batch.id,
        movement_type=movement_type, quantity=quantity, notes=notes.strip() or None
    ))
    db.commit()
    return RedirectResponse(url="/movimentacoes", status_code=303)


@router.post("/lotes")
def create_batch(
    product_id: int = Form(...),
    code: str = Form(...),
    quantity: int = Form(...),
    received_at: date = Form(...),
    expires_at: date = Form(...),
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)
    if product is None or quantity < 0 or expires_at < received_at:
        return RedirectResponse(url="/movimentacoes?erro=lote", status_code=303)
    db.add(Batch(
        product_id=product_id, code=code.strip(), quantity=quantity,
        received_at=received_at, expires_at=expires_at
    ))
    db.commit()
    return RedirectResponse(url="/movimentacoes", status_code=303)
