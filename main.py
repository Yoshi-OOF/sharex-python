from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.security import APIKeyHeader
from fastapi.responses import PlainTextResponse, FileResponse

import os
import random
import string
import yaml


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
async def post_file(file: UploadFile = File(...), api_key: str = Depends(check_api_key)):
    content = await file.read()

    # If the file size is greater than the maximum file size
    if config["max_file_size"] > -1 and len(content) > 1000000 and config["max_file_size"]:
        raise HTTPException(status_code=413, detail="File too large >:(")

    # Retrieve file extension
    extension = os.path.splitext(file.filename)[1]

    # Generate a random file name (32 characters)
    file_name = ''.join(random.choices(string.ascii_letters + string.digits, k=config["filename_size"]))

    # Choosing where to save the file
    file_path = f"{upload_dir}/{file_name}{extension}"

    # Write the file to the specified location
    with open(file_path, "wb") as file_object:
        file_object.write(content)

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