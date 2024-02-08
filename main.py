from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.security import APIKeyHeader
import os
import random
import string
import yaml


# Load the configuration file
config = yaml.load(open("config.yml"), Loader=yaml.FullLoader)


# Add a trailing slash if it's not present
url = config["url"] + "" if config["url"][-1] == "/" else "/"


# Create the upload directory if it doesn't exist
upload_dir = config["upload_directory"]
os.makedirs(upload_dir, exist_ok=True)


# Create a FastAPI instance
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

    # If the file size is greater than the maximum file size
    if config["max_file_size"] > -1 and len(content) > 1000000 and config["max_file_size"]:
        raise HTTPException(status_code=413, detail="File too large >:(")

    # Retrieve file extension
    extension = os.path.splitext(file.filename)[1]
    file_name = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    file_path = f"uploads/{file_name}{extension}"

    # Generate a random file name (32 characters)
    file_name = ''.join(random.choices(string.ascii_letters + string.digits, k=config["filename_size"]))

    # Choosing where to save the file
    file_path = f"{upload_dir}/{file_name}{extension}"

    # Write the file to the specified location
    with open(file_path, "wb") as file_object:
        file_object.write(content)

    # Return the URL of the uploaded file
    return f'{url}{file_name}{extension}'


    file_path = f"{upload_dir}/{file_id}"
if __name__ == "__main__":
    import uvicorn
    print("Running the ShareX server.")
    uvicorn.run(app,
                host=config["internal_host"],
                port=config["internal_port"],
                log_level=config["log_level"]
                )