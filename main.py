from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.security import APIKeyHeader
import os
app = FastAPI()
os.makedirs("uploads", exist_ok=True)

SECRET_KEY = "met_ta_key_ici_bibou"

api_key_header = APIKeyHeader(name="X-API-Key")

async def check_api_key(api_key: str = Depends(api_key_header)):
    if api_key != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return api_key

@app.post("/")
async def post_file(file: UploadFile = File(...), api_key: str = Depends(check_api_key)):
    content = await file.read()
    with open(f"uploads/{file.filename}", "wb") as file_object:
        file_object.write(content)

@app.get("/{fileId}")
async def get_file(name: str):
    return {"message": f"Hello {name}"}
