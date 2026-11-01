from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from ..models import Batch


def get_expiry_batches(db: Session, reference_date: date | None = None, days: int = 7):
    today = reference_date or date.today()
    limit_date = today + timedelta(days=days)
    return db.scalars(
        select(Batch)
        .options(joinedload(Batch.product))
        .where(Batch.quantity > 0, Batch.expires_at <= limit_date)
        .order_by(Batch.expires_at)
    ).all()
