import traceback
from datetime import timezone, datetime
import time

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from icalendar import Calendar as Icalendar
import pytz

from config import get_db

from model import Calendars, User, EventMain, EventDetail, Alarm, FailedImportEvent, ImportCalendar
from .import_module import get_calendar, get_alarm, get_event_main, get_event_detail
from dto import ImportResonseDTO

router = APIRouter()

@router.post("/import")
async def import_data(user_id: int, ics_file: UploadFile = File(...), db: Session = Depends(get_db)) -> ImportResonseDTO:
    """
    iCalendar 파일과 user id를 입력으로 받아, 해당 유저의 캘린더를 생성하고 ics 파일을 저장한 뒤, 실행 과정에 대한 로그를 쌓는다.
    
    입력으로 받은 ics 파일은 무조건 저장
        
    캘린더를 추출하는 데에 실패할 경우, 완전 실패로 처리하여 에러를 반환
    
    개별 이벤트 추출에서 에러가 발생할 경우, event_main이 이미 만들어졌어도(flush) 롤백함
    
    이벤트 내부의 알람은 최상위 하나만 가져오며, 에러가 발생하면 이벤트 생성은 진행하나, 연결된 알람이 없는 채로 생성됨
    
    :param user_id: 유저의 id, int값. 외부에 유출되지 않도록 유의
    :param ics_file: icalendar 형식의 파일
    """
    start_time = time.time()
    
    ics_file_content = await ics_file.read()
    
    cal = Icalendar.from_ical(ics_file_content)
    
    #TODO ics 파일 저장
    
    # 캘린더 추출에서 성공/실패 여부 상관 없이 ImportCalendar에 대한 로그 생성
    try:
        # 캘린더 추출
        calendar, tz = get_calendar(cal, user_id)
        
        # 이미 추가된 캘린더인지 확인하기
        legacy_calendar = db.query(Calendars).filter_by(user_id=user_id, title=calendar.title).first()
        
        # 이미 추가되었으면 레거시 캘린더를 수정하여 덮어씌우기
        if legacy_calendar:
            legacy_calendar.description = calendar.description
            legacy_calendar.timezone_id = calendar.timezone_id
            legacy_calendar.is_deleted = 0
            
            # 추출한 캘린더 메모리 해제 후, 새로 할당
            del calendar
            calendar = legacy_calendar
        
        # 새로 만들 경우, db에 flush하여 id 생성
        else:
            db.add(calendar)
            db.flush()
            
        calendar_id = calendar.calendar_id
        import_calendar = ImportCalendar(calendar_id = calendar_id,
                # ics_file_path =
                
                # TODO s3로 삽입
                )
        
        db.add(import_calendar)
        db.commit()
        
    except:
        # 실패 시, 이전 동작에 대한 롤백 진행 후 예외 반환
        db.rollback()
        import_calendar = ImportCalendar(is_success = 0,
                                         # ics_file_path = 
                                         )
        db.add(import_calendar)
        db.commit()
        raise HTTPException(422, detail="캘린더 생성 실패")
    
    import_id = import_calendar.import_id
    
    # 추출 성공 / 살패 카운터 초기화
    event_cnt = 0
    fail_cnt = 0
    
    for component in cal.walk():
        if component.name == 'VEVENT':
            uid = component.get("UID")
            legacy_event_detail = db.query(EventDetail).filter_by(uid=uid).first()
            # 레거시 데이터가 존재할 경우
            if legacy_event_detail:
                try:
                    legacy_event_main: EventMain = legacy_event_detail.event_main
                    new_event_main: EventMain = get_event_main(component, calendar_id)
                    
                    legacy_event_main.summary = new_event_main.summary
                    legacy_event_main.start_at = new_event_main.start_at
                    legacy_event_main.end_at = new_event_main.end_at
                    legacy_event_main.priority = new_event_main.priority
                    legacy_event_main.repeat_rule = new_event_main.repeat_rule
                    legacy_event_main.is_deleted = 0
                    
                    # 알람 초기화 후, 이전 데이터가 존재할 경우 덮어 씌우기
                    alarm = None
                    if legacy_event_detail.alarm:
                        alarm = legacy_event_detail.alarm
                        
                    # 데이터가 없을 경우 새로 생성해서 삽입
                    else:
                        for sub_com in component.subcomponents:
                            if sub_com.name == "VALARM":
                                try:
                                    alarm = get_alarm(sub_com)
                                    db.add(alarm)
                                    db.flush()
                                except:
                                    alarm = None
                                finally:
                                    break
                    
                    # 이벤트 디테일은 이미 존재하는 것을 확인했으므로, 수정 사항 덮어 씌우기
                    event_detail : EventDetail = get_event_detail(component, event_main, alarm, tz)
                    legacy_event_detail.alarm = alarm
                    legacy_event_detail.description = event_detail.description
                    legacy_event_detail.location = event_detail.location
                    legacy_event_detail.sequence = event_detail.sequence
                    legacy_event_detail.status = event_detail.status
                    legacy_event_detail.transp = event_detail.transp
                    
                    event_cnt += 1
                except:
                    db.rollback()
                    
                    error_trace = traceback.format_exc().replace("\n", "").replace("  ", " ")
                    error_log = error_trace[error_trace.index("line"):]    
                    failed_import_event = FailedImportEvent(import_id = import_id,
                                                            log = error_log)
                    
                    fail_cnt += 1
                    
                    db.add(failed_import_event)
                
                # 변경 사항 저장
                db.commit()
                
            # 이전 데이터가 존재하지 않는 경우
            else:
                try:
                    # event main 부터 새로 생성
                    event_main = get_event_main(component, calendar_id, tz)
                    db.add(event_main)
                    db.flush()
                
                    # alarm은 None으로 초기화 후, 값이 생길 경우 db에 flush
                    alarm = None
                    for sub_com in component.subcomponents:
                        if sub_com.name == "VALARM":
                            try:
                                alarm = get_alarm(sub_com)
                                db.add(alarm)
                                db.flush()
                            except:
                                alarm = None
                            finally:
                                break
                    
                    # event detail 새로 만들기
                    event_detail = get_event_detail(component, event_main, alarm, tz)
                    
                    db.add(event_detail)
                    db.commit()
                    
                    event_cnt += 1
                    
                except:
                    error_trace = traceback.format_exc().replace("\n", "").replace("  ", " ")
                    error_log = error_trace[error_trace.index("line"):]
                    
                    db.rollback()
                    
                    failed_import_event = FailedImportEvent(import_id = import_id,
                                                            log = error_log)
                    
                    fail_cnt += 1
                    
                    db.add(failed_import_event)
                    db.commit()

    # import log에 성공 / 실패 카운트 삽입
    import_calendar.event_count = event_cnt
    import_calendar.fail_count = fail_cnt
    
    # import에 소요된 시간 적재
    time_taken = round(time.time() - start_time, 4)
    import_calendar.time_taken = time_taken
    
    # 최종 커밋
    db.commit()
    
    # 결과 사항 반환
    result = ImportResonseDTO(calendarId=calendar_id,
                              eventCount=event_cnt,
                              failCount=fail_cnt,
                              takenTime=time_taken)
    
    return JSONResponse(content=result.__dict__, status_code=201)