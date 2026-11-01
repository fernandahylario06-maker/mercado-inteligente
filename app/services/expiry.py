
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..models import Batch


def get_expiry_batches(
    db: Session,
    reference_date: date | None = None,
    days: int = 7,
):
    """
    Retorna lotes com saldo positivo e vencimento até
    o limite de dias informado, incluindo lotes vencidos.
    """

    if days < 0:
        raise ValueError("O período de dias não pode ser negativo.")

    today = reference_date or date.today()
    limit_date = today + timedelta(days=days)

    statement = (
        select(Batch)
        .options(joinedload(Batch.product))
        .where(
            Batch.quantity > 0,
            Batch.expires_at <= limit_date,
        )
        .order_by(Batch.expires_at)
    )

    return db.scalars(statement).all()
