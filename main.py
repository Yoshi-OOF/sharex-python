from fastapi import FastAPI

app = FastAPI()


@app.post("/")
async def post_file():
    return {"message": "Hello World"}


@app.get("/{fileId}")
async def get_file(name: str):
    return {"message": f"Hello {name}"}
