from typing import Tuple, Union
from datetime import date, datetime

from fastapi import HTTPException
from icalendar import Calendar as Icalendar
from sqlalchemy.orm import Session
import pytz

from model import Calendars, ImportCalendar, Alarm, EventMain, EventDetail

def get_calendar(cal: Icalendar, user_id) -> Tuple[Calendars, pytz.BaseTzInfo]:
    """
    icalendar 파일로부터 캘린더 추출
    
    ics 파일 하나에는 반드시 1개만의 캘린더 정보가 포함되어야만 함
    
    추출한 캘린더를 엔티티 객체로 만들어, 타임존과 함께 튜플 형식으로 반환
    """
    for component in cal.walk():
        if component.name == "VCALENDAR":
            cal_prod_id = str(component.get("PRODID"))
            cal_name = str(component.get("X-WR-CALNAME"))
            cal_tz = str(component.get("X-WR-TIMEZONE"))
            break
    
    calendar = Calendars(title = cal_name,
            prod_id = cal_prod_id,
            timezone_id = cal_tz,
            user_id = user_id,
            color_set_id = 1)
    
    tz = pytz.timezone(cal_tz)
    
    return (calendar, tz)


def get_event_main(component: Icalendar, calendar_id : int, tz: pytz.BaseTzInfo) -> EventMain:
    """
    event main 추출
    
    DTSTART, DTEND에서 가장 많은 예외가 발생할 것으로 보임.
    
    datatime, date 타입이 섞여있으며, date인 경우, 타임존을 적용하지 않음.
    
    Asia/Seoul;2024-09-01T00:00:00; - 시간 변환 시 알아서 적용
    
    2024-01-01T00:00:00Z; - 접미어 Z가 붙은 경우, UTC 시간으로, 타임존을 적용하여 시간을 맞춰줘야 함.
    
    2024-01-01; - date 타입으로, 시간 단위가 아닌 일 단위 일정의 경우 이렇게 표기 됨.
    """
    summary = str(component.get("SUMMARY"))
    start_at = component.get("DTSTART").dt
    if type(start_at) == datetime:
        start_at = start_at.astimezone(tz)
    end_at = component.get("DTEND").dt
    if type(end_at) == datetime:
        end_at = end_at.astimezone(tz)

    priority = int(component.get("PRIORITY")) if component.get("PRIORITY") else 5
    repeat_rule = str(component.get("RRULE").to_ical())[2:-1] if component.get("RRULE") else None

    event_main = EventMain(
        summary = summary,
        start_at = start_at,
        end_at = end_at,
        priority = priority,
        repeat_rule = repeat_rule,
        calendar_id = calendar_id)    
    
    return event_main


def get_event_detail(component: Icalendar, event_main: EventMain, alarm: Alarm, tz: pytz.BaseTzInfo) ->  EventDetail:
    """
    event detail을 추출, 생성하여 반환
    
    모두 표준 규격에 맞춰져 있고, 별도의 타입 변환이나 케이스 조절이 필요없음.
    
    대부분의 경우에서 에러가 발생하지 않겠으나, UID가 unique이므로, 반영이 안 될 수도 있음.
    """
    created_at = component.get("CREATED").dt.astimezone(tz)
    last_modified = component.get("LAST-MODIFIED").dt.astimezone(tz)
    event_description = str(component.get("DESCRIPTION"))
    sequence = str(component.get("SEQUENCE"))
    status = str(component.get("STATUS"))
    transp = str(component.get("TRANSP"))
    location = str(component.get("LOCATION"))
    uid = str(component.get("UID"))

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
    
    return event_detail

def get_alarm(component : Icalendar, db : Session) -> Alarm | None:
    """
    Alarm 객체를 생성함
    
    기본적으로 표준 규격에 따르는 값 밖에 없으므로 큰 걱정은 없지만, 가끔 이상한 값이 들어옴.
    
    그럴 경우 예외로 처리하고, none을 반환하여 연결된 알람을 없는 것으로 만듦.
    """
    for sub_com in component.subcomponents:
        if sub_com.name == "VALARM":
            try:
                action = str(sub_com.get("ACTION"))
                if action == "NONE":
                    return None
                trigger = str(sub_com.get("TRIGGER").to_ical())[2:-1]
                alarm_description = str(sub_com.get("DESCRIPTION"))
                alarm = Alarm(action = action,
                    description = alarm_description,
                    alarm_trigger = trigger)
                db.add(alarm)
                db.flush()
                return alarm
            except:
                alarm = None
                break