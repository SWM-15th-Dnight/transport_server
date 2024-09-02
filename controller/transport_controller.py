from datetime import timezone, datetime

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from icalendar import Calendar as Icalendar
import pytz

from config import get_db
from service import TransportService

from model import Calendar, User, EventMain, EventDetail, Alarm

router = APIRouter()

@router.post("/")
async def import_data(user_id: int, ics_file: UploadFile = File(...), db: Session = Depends(get_db)):
    
    ics_file_content = await ics_file.read()
    
    cal = Icalendar.from_ical(ics_file_content)
    
    for component in cal.walk():
        if component.name == "VCALENDAR":
            cal_prod_id = str(component.get("PRODID"))
            cal_name = str(component.get("X-WR-CALNAME"))
            cal_tz = str(component.get("X-WR-TIMEZONE"))
            break
    
    calendar = Calendar(title = cal_name,
             prod_id = cal_prod_id,
             timezone_id = cal_tz,
             user_id = user_id,
             color_set_id = 1)
    
    tz = pytz.timezone(cal_tz)
    
    db.add(calendar)
    db.commit()
    
    calenadr_id = calendar.calendar_id
    
    for component in cal.walk():
        if component.name == 'VEVENT':
            summary = str(component.get("SUMMARY"))
            start_at = component.get("DTSTART").dt
            if type(start_at) == datetime:
                start_at = start_at.astimezone(tz)
            end_at = component.get("DTEND").dt
            if type(end_at) == datetime:
                end_at = end_at.astimezone(tz)
            created_at = component.get("CREATED").dt.astimezone(tz)
            last_modified = component.get("LAST-MODIFIED").dt.astimezone(tz)
            event_description = str(component.get("DESCRIPTION"))
            sequence = str(component.get("SEQUENCE"))
            status = str(component.get("STATUS"))
            transp = str(component.get("TRANSP"))
            location = str(component.get("LOCATION"))
            priority = int(component.get("PRIORITY")) if component.get("PRIORITY") else 5
            repeat_rule = str(component.get("RRULE").to_ical())[2:-1] if component.get("RRULE") else None
            uid = str(component.get("UID"))

            event_main = EventMain(
                summary = summary,
                start_at = start_at,
                end_at = end_at,
                priority = priority,
                repeat_rule = repeat_rule,
                calendar_id = calenadr_id)
            db.add(event_main)
            db.commit()
            
            alarm = None
            
            for sub_com in component.subcomponents:
                if sub_com.name == "VALARM":
                    action = str(sub_com.get("ACTION"))
                    if action == "NONE":
                        break
                    trigger = str(sub_com.get("TRIGGER").to_ical())[2:-1]
                    alarm_description = str(sub_com.get("DESCRIPTION"))
                    alarm = Alarm(action = action,
                          description = alarm_description,
                          alarm_trigger = trigger)
                    db.add(alarm)
                    db.commit()
                    break
            
            event_detail = EventDetail(
                event_detail_id = event_main.event_id,
                uid = uid,
                sequence = sequence,
                description = event_description,
                location = location,
                status = status,
                transp = transp,
                input_time_taken = 0,
                created_at = created_at,
                updated_at = last_modified,
                
                alarm_id = alarm.alarm_id if alarm else None,
                input_type_id = 11
            )
            
            db.add(event_detail)
            db.commit()