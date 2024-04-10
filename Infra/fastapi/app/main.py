from fastapi import FastAPI

app = FastAPI()

# docs에서 확인가능
@app.get("/")
def read_root():
    return {"Hello": "World"}
