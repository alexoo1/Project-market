import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.order import OrderPublic, PurchaseRequest
from app.services.order_service import OrderService

router = APIRouter(tags=["orders"])


@router.post(
    "/listings/{listing_id}/purchase", response_model=OrderPublic, status_code=status.HTTP_201_CREATED
)
def purchase_listing(
    listing_id: uuid.UUID,
    payload: PurchaseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Achat direct au prix affiché de l'annonce."""
    service = OrderService(db)
    order = service.create_order_from_listing(current_user.id, listing_id, payload)
    return service.get_order(order.id, current_user.id)


@router.post("/offers/{offer_id}/purchase", response_model=OrderPublic, status_code=status.HTTP_201_CREATED)
def purchase_from_offer(
    offer_id: uuid.UUID,
    payload: PurchaseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Achat au montant d'une offre préalablement acceptée par le vendeur."""
    service = OrderService(db)
    order = service.create_order_from_offer(current_user.id, offer_id, payload)
    return service.get_order(order.id, current_user.id)


@router.get("/orders/mine/purchases", response_model=list[OrderPublic])
def list_my_purchases(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return OrderService(db).list_my_purchases(current_user.id)


@router.get("/orders/mine/sales", response_model=list[OrderPublic])
def list_my_sales(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return OrderService(db).list_my_sales(current_user.id)


@router.get("/orders/{order_id}", response_model=OrderPublic)
def get_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return OrderService(db).get_order(order_id, current_user.id)


@router.post("/orders/{order_id}/pay", response_model=OrderPublic)
def pay_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return OrderService(db).pay_order(order_id, current_user.id)


@router.post("/orders/{order_id}/ship", response_model=OrderPublic)
def ship_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return OrderService(db).ship_order(order_id, current_user.id)


@router.post("/orders/{order_id}/confirm-receipt", response_model=OrderPublic)
def confirm_receipt(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return OrderService(db).confirm_receipt(order_id, current_user.id)


@router.post("/orders/{order_id}/cancel", response_model=OrderPublic)
def cancel_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return OrderService(db).cancel_order(order_id, current_user.id)
