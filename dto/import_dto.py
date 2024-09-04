from pydantic import BaseModel

class ImportResonseDTO(BaseModel):
    
    calendarId : int
    eventCount : int
    failCount : int
    takenTime : float