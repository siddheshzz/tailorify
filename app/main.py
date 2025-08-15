from fastapi import FastAPI , Request


app = FastAPI()


@app.get("/")
def root(request:Request):
    return {"msg" : "hello this is home", "status": 200}


