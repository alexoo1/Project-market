import uuid

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.order import Order


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, order: Order) -> Order:
        self.db.add(order)
        self.db.flush()
        return order

    def get_by_id(self, order_id: uuid.UUID, with_relations: bool = False) -> Order | None:
        stmt = select(Order).where(Order.id == order_id)
        if with_relations:
            stmt = stmt.options(joinedload(Order.payment), joinedload(Order.delivery))
        return self.db.scalar(stmt)

    def save(self, order: Order) -> Order:
        self.db.add(order)
        self.db.flush()
        return order

    def list_for_buyer(self, buyer_id: uuid.UUID) -> list[Order]:
        stmt = (
            select(Order)
            .where(Order.buyer_id == buyer_id)
            .options(joinedload(Order.payment), joinedload(Order.delivery))
            .order_by(Order.created_at.desc())
        )
        return list(self.db.scalars(stmt).unique())

    def list_for_seller(self, seller_id: uuid.UUID) -> list[Order]:
        stmt = (
            select(Order)
            .where(Order.seller_id == seller_id)
            .options(joinedload(Order.payment), joinedload(Order.delivery))
            .order_by(Order.created_at.desc())
        )
        return list(self.db.scalars(stmt).unique())
