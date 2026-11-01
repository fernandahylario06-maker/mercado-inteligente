
from datetime import date

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.expiry import get_expiry_batches


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/alertas")
def expiry_alerts(
    request: Request,
    db: Session = Depends(get_db),
):
    # Define uma única data de referência para os alertas.
    today = date.today()

    # Consulta os lotes considerando a data definida.
    batches = get_expiry_batches(
        db,
        reference_date=today,
    )

    return templates.TemplateResponse(
        request=request,
        name="alerts.html",
        context={
            "batches": batches,
            "today": today,
        },
    )
