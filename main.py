from typing import Annotated

from fastapi import FastAPI, UploadFile, File

app = FastAPI()

@app.post("/")
async def post_file(file: Annotated[bytes, File()]):
    content = file.decode("utf-8")
    return {"file_content": content}

@app.get("/{fileId}")
async def get_file(name: str):
    return {"message": f"Hello {name}"}
