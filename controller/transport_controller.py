from fastapi import APIRouter
from sqlalchemy.orm import Session


from config import get_db
from service import TransportService

router = APIRouter()


@router.get("/")
def get_transport(db: Session):
    
    db.query()