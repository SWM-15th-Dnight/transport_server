import os
from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
import pytz

from config import get_db

from model import Calendars, User, EventMain, EventDetail, Alarm, ExportCalendar
from .s3_module import s3_bucket


router = APIRouter()

ICS_DUMP_DIR_PATH = os.path.dirname(__file__) + "/../" + "ics_dump/"

@router.get("/export", status_code=200, response_class=FileResponse)
def ics_export(user_id : int, calendar_id : int, db : Session = Depends(get_db)):
    """
    유저의 id와 calendar_id를 기반으로, 해당 calendar를 ics로 바꾸어 반환함.
    
    private 서브넷의 prod 환경에서는 반드시 spring을 통해야만 사용할 수 있음.
    
    spring 서버로 ics 파일 자체를 반환하여, spring에서는 s3를 통할 필요가 없도록 만들었음.
    
    반환되는 ics 파일은 유저 이메일-캘린더 이름.ics 형식임.
    
    ex) admin@calinifay-Test_calendar.ics
    """
    
    calendar : None | Calendars = db.query(Calendars).get(calendar_id)
    user : None | User = db.query(User).get(user_id)
    
    if not calendar or not user or calendar.is_deleted:
        return HTTPException(404, "캘린더 또는 유저가 없습니다!")
    
    ics_file_name = f"{user.email}-{calendar.title}.ics"
    
    # 캘린더 시작 
    ics_buf = f"""BEGIN:VCALENDAR
    PRODID:{calendar.prod_id}
    VERSION:2.0
    CALSCALE:GREGORIAN
    METHOD:PUBLISH
    X-WR-CALNAME:{user.email}
    X-WR-TIMEZONE:{calendar.timezone_id}
    """.replace("    ", "")
    
    # event main, event detail, alarm을 조인하여 한 번의 쿼리로 데이터 가져오기
    events : list[EventMain] = db.query(EventMain).filter(EventMain.calendar_id == calendar_id).options(
        joinedload(EventMain.event_detail).
        joinedload(EventDetail.alarm)).all()
    
    # 이벤트 개수 카운트 초기화
    e_count = 0
    
    if not events:
        return HTTPException(404, "캘린더가 비어 있습니다!")
    
    for em in events:
        
        # n번째 이벤트 입력
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

        # 옵션 항목인 설명과 장소는 있는 경우만 기입
        description = f"DESCRIPTION:{ed.description}\n" if ed.description else ""
        location = f"LOCATION:{ed.location}\n" if ed.location else ""
        
        ev_buf += description + location
        
        # 연결된 알람이 존재할 경우 입력
        if ed.alarm:
            alarm : Alarm = ed.alarm
            al_buf = f"""BEGIN:VALARM
            ACTION:{alarm.action.value}
            TRIGGER:{alarm.alarm_trigger}
            """.replace("            ", "")
            
            al_desc = f"DESCRIPTION:{alarm.description}\n" if alarm.description else ""
            
            # 이벤트에 알람 본문 추가
            ev_buf += al_buf + al_desc + "END:VALARM\n"

        # n번째 이벤트 끝, 캘린더 본문에 이벤트 추가
        ics_buf += ev_buf + "END:VEVENT\n"
        e_count += 1
    
    # 캘린더 끝
    ics_buf += "END:VCALENDAR"
    
    # 서버 로컬에 파일 저장
    with open(ICS_DUMP_DIR_PATH+ics_file_name, '+w') as f:
        f.write(ics_buf)

    # 방금 저장한 파일 읽어서 S3에 등록
    with open(ICS_DUMP_DIR_PATH+ics_file_name, 'rb') as f:
        s3_bucket.upload_file(f, ics_file_name, T="export")
    
    # export에 대한 로그 생성
    export_calendar = ExportCalendar(event_count = e_count,
                   export_uid = ics_file_name,
                   calendar_id = calendar_id)
    
    db.add(export_calendar)
    db.commit()
    db.close()
    
    return FileResponse(ICS_DUMP_DIR_PATH+ics_file_name, media_type="text/plain", filename=ics_file_name)

# 각각의 타임존을 UTC로 통일
def timezone_nomalize(date: datetime, timezone : str):
    
    local_tz = pytz.timezone(timezone)
    local_dt = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S")
    local_dt = local_tz.localize(local_dt)
    utc_dt = local_dt.astimezone(pytz.utc)
    
    return utc_dt.strftime("%Y%m%dT%H%M%SZ")