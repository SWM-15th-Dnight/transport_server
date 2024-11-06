import os
from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
import pytz

from config import get_db

from model import Calendars, User, EventMain, EventDetail, Alarm, ExportCalendar
from .s3_module import s3_bucket


router = APIRouter()

ICS_DUMP_DIR_PATH = os.path.dirname(__file__) + "/../" + "ics_dump"

@router.get("/export", status_code=201)
def ics_export(user_id : int, calendar_id : int, db : Session = Depends(get_db)):
    
    calendar : None | Calendars = db.query(Calendars).get(calendar_id)
    user : None | User = db.query(User).get(user_id)
    
    if not calendar or not user or calendar.is_deleted:
        return HTTPException(404, "캘린더 또는 유저가 없습니다!")
    
    ics_file_name = str(uuid.uuid4()) + ".ics"
    
    ics_buf = f"""BEGIN:VCALENDAR
    PRODID:{calendar.prod_id}
    VERSION:2.0
    CALSCALE:GREGORIAN
    METHOD:PUBLISH
    X-WR-CALNAME:{user.email}
    X-WR-TIMEZONE:{calendar.timezone_id}
    """.replace("    ", "")
    
    events : list[EventMain] = db.query(EventMain).filter(EventMain.calendar_id == calendar_id).options(
        joinedload(EventMain.event_detail)).all()
    
    e_count = 0
    
    if not events:
        return HTTPException(404, "캘린더가 비어 있습니다!")
    
    for em in events:
        
        if em.is_deleted:
            continue
        
        ed : EventDetail = em.event_detail
        
        tz = calendar.timezone_id
        
        start_at = timezone_nomalize(em.start_at, tz)
        end_at = timezone_nomalize(em.end_at, tz)
        created_at = timezone_nomalize(ed.created_at, tz)
        updated_at = timezone_nomalize(ed.updated_at, tz)
        
        ev_buf = f"""BEGIN:VEVENT
        DTSTART:{start_at}
        DTEND:{end_at}
        DTSTAMP:{created_at}
        LAST-MODIFIED:{updated_at}
        SUMMARY:{em.summary}
        UID:{ed.uid}
        SEQUENCE:{ed.sequence}
        STATUS:{ed.status.value}
        TRANSP:{ed.transp.value}
        """.replace("        ", "")
    
        description = f"DESCRIPTION:{ed.description}\n" if ed.description else ""
        location = f"LOCATION:{ed.location}\n" if ed.location else ""
        
        ev_buf += description + location
        
        if ed.alarm:
            alarm : Alarm = ed.alarm
            al_buf = f"""BEGIN:VALARM
            ACTION:{alarm.action.value}
            TRIGGER:{alarm.alarm_trigger}
            """.replace("            ", "")
            
            al_desc = f"DESCRIPTION:{alarm.description}\n" if alarm.description else ""
            
            ev_buf += al_buf + al_desc + "END:VALARM\n"
        
        ev_buf += "END:VEVENT\n"
        
        
        ics_buf += ev_buf
        e_count += 1
    
    ics_buf += "END:VCALENDAR"
    
    # 테스트용
    with open(ICS_DUMP_DIR_PATH+ics_file_name, '+w') as f:
        f.write(ics_buf)
        f.close()

    with open(ICS_DUMP_DIR_PATH+ics_file_name, 'rb') as f:
        s3_bucket.upload_file(f, ics_file_name, T="export")
    
    export_calendar = ExportCalendar(event_count = e_count,
                   export_uid = ics_file_name,
                   calendar_id = calendar_id)
    
    db.add(export_calendar)
    db.commit()
    db.close()

    return {"ics_file_name" : ics_file_name}

def timezone_nomalize(date: datetime, timezone : str):
    
    local_tz = pytz.timezone(timezone)
    local_dt = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S")
    local_dt = local_tz.localize(local_dt)
    utc_dt = local_dt.astimezone(pytz.utc)
    
    return utc_dt.strftime("%Y%m%dT%H%M%SZ")