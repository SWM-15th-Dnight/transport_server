import uvicorn
from fastapi import FastAPI

from apis import import_ics, export_ics

app = FastAPI()

app.include_router(import_ics, prefix="/api/v1", tags=["event_transport"])
app.include_router(export_ics, prefix="/api/v1", tags=["event_transport"])

@app.get("/")
def index():
    return {"hello" : "world"}


if __name__ == "__main__" :
    
    import os
    profile = os.environ.get("CALINIFY_TRANSPORT_SERVER_PROFILE")
    if profile in ["PROD", "DEV"] :
        raise RuntimeError(
            "운영 및 배포 환경에서는 반드시 터미널로 uvicorn을 동작시켜야 합니다."
        )
    uvicorn.run("app:app", host="127.0.0.1", port=5051, reload=True)