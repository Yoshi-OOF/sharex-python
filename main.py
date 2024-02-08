from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.security import APIKeyHeader
import os
import random
import string
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
    extension = os.path.splitext(file.filename)[1]
    file_name = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    file_path = f"uploads/{file_name}{extension}"
    with open(file_path, "wb") as file_object:
        file_object.write(content)
    return {
        "file_name": file_name,
        "extension": extension,
        "file_path": file_path
    }

@app.get("/{fileId}")
async def get_file(name: str):
    return {"message": f"Hello {name}"}

if __name__ == "__main__":
    import uvicorn
    print("Running the ShareX server.")
    uvicorn.run(app,
                host=config["internal_host"],
                port=config["internal_port"],
                log_level=config["log_level"]
                )