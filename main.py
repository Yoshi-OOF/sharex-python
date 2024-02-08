import os
import random
import string

import aiofiles
import fastapi
import yaml
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import PlainTextResponse, FileResponse
from fastapi.security import APIKeyHeader


# Load the configuration file
config = yaml.load(open("config.yml"), Loader=yaml.FullLoader)


# Add a trailing slash if it's not present
url = config["url"] + ("" if config["url"][-1] == "/" else "/")



# Create the upload directory if it doesn't exist
upload_dir = config["upload_directory"]
os.makedirs(upload_dir, exist_ok=True)


# Create a FastAPI instance
app = FastAPI()
api_key_header = APIKeyHeader(name="secret-key", auto_error=False)


async def check_api_key(api_key: str = Depends(api_key_header)):

    # If the secret key is not provided
    if api_key is None or api_key == "":
        # 401 Unauthorized
        raise HTTPException(status_code=401, detail="Secret Key is missing >:(")

    # If the secret key is incorrect
    if api_key != config["secret_key"]:
        # 403 Forbidden
        raise HTTPException(status_code=403, detail="Invalid secret Key >:(")
    return api_key


@app.post("/", response_class=PlainTextResponse)
async def post_file(request: fastapi.Request, api_key: str = Depends(check_api_key)):


    # Retrieve file extension
    #extension = os.path.splitext(file.filename)[1]
    extension = ".png"

    # Generate a random file name (32 characters)
    file_name = ''.join(random.choices(string.ascii_letters + string.digits, k=config["filename_size"]))

    # Choosing where to save the file
    file_path = f"{upload_dir}/{file_name}{extension}"

    async with aiofiles.open(file_path, 'wb') as buffer:
        async for chunk in request.stream():
            await buffer.write(chunk)

    # Return the URL of the uploaded file
    return f"{url}{file_name}{extension}"


@app.get("/{file_id}")
async def get_file(file_id):
    # Check if the file exists
    file_path = f"{upload_dir}/{file_id}"

    # If the file does not exist
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found >:(")

    # Return the file
    return FileResponse(file_path)


if __name__ == "__main__":
    import uvicorn
    print("Running the ShareX server.")
    uvicorn.run(app,
                host=config["internal_host"],
                port=config["internal_port"],
                log_level=config["log_level"]
                )