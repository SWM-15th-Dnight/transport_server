from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config import get_db
from service import TransportService

from model import Calendar, User, EventMain, EventDetail, Alarm

router = APIRouter()

@router.get("/")
def get_transport(db: Session = Depends(get_db)):
    
    calendars = db.query(Calendar).all()
    user = db.query(User).all()
    event_main = db.query(EventMain).all()
    event_detail = db.query(EventDetail).all()
    alarm = db.query(Alarm).all()
    
    return {"cal" : calendars, "user" : user, "event_m" : event_main, "event_d" : event_detail, "alarm" : alarm}