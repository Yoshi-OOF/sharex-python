from fastapi import FastAPI, UploadFile, File
import os

app = FastAPI()
os.makedirs("uploads", exist_ok=True)

@app.post("/")
async def post_file(file: UploadFile = File(...)):
    content = await file.read()
    with open(f"uploads/{file.filename}", "wb") as file_object:
        file_object.write(content)

@app.get("/{fileId}")
async def get_file(name: str):
    return {"message": f"Hello {name}"}
