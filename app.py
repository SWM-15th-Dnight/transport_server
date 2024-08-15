import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def index():
    return {"hello" : "world"}


if __name__ == "__main__" :
    uvicorn.run("app:app", host="127.0.0.1", port=5051, reload=True)