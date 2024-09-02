import uvicorn
from fastapi import FastAPI

from controller import transport_router

app = FastAPI()

app.include_router(transport_router, prefix="/api/v1", tags=["event_transport"])

@app.get("/")
def index():
    return {"hello" : "world"}


if __name__ == "__main__" :
    uvicorn.run("app:app", host="127.0.0.1", port=5051, reload=True)