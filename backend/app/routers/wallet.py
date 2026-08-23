from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.wallet import WalletPublic, WalletTransactionPublic, WithdrawalRequest
from app.services.wallet_service import WalletService

router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.get("", response_model=WalletPublic)
def get_wallet(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = WalletService(db)
    wallet = service.get_or_create_wallet(current_user.id, with_transactions=True)
    db.commit()
    return wallet


@router.post("/withdrawals", response_model=WalletTransactionPublic)
def request_withdrawal(
    payload: WithdrawalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = WalletService(db)
    return service.request_withdrawal(
        current_user.id, payload.method, payload.destination, payload.amount
    )
