from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.brand_repository import BrandRepository
from app.repositories.category_repository import CategoryRepository
from app.schemas.taxonomy import BrandPublic, CategoryPublic

router = APIRouter(tags=["taxonomy"])


@router.get("/categories", response_model=list[CategoryPublic])
def list_categories(db: Session = Depends(get_db)):
    return CategoryRepository(db).list_all()


@router.get("/brands", response_model=list[BrandPublic])
def list_brands(db: Session = Depends(get_db)):
    return BrandRepository(db).list_all()
