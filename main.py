from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Request
from fastapi.security import APIKeyHeader
from fastapi.responses import PlainTextResponse, FileResponse

from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget, ValueTarget
from streaming_form_data.validators import MaxSizeValidator
import streaming_form_data

from starlette.requests import ClientDisconnect

import os
import random
import string
import yaml

from classes import *


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

async def process_file(request: Request):
    body_validator = MaxBodySizeValidator(config["max_file_size"])
    filename = request.headers.get('Filename')

    if not filename:
        raise HTTPException(status_code=422,
                            detail='Filename header is missing')
    try:
        file_extension = os.path.splitext(filename)[1]
        file_name = ''.join(random.choices(string.ascii_letters + string.digits, k=config["filename_size"]))
        filepath = f"{upload_dir}/{file_name}{file_extension}"
        file_ = FileTarget(filepath, validator=MaxSizeValidator(config["max_file_size"]))
        data = ValueTarget()
        parser = StreamingFormDataParser(headers=request.headers)
        parser.register('file', file_)
        parser.register('data', data)

        async for chunk in request.stream():
            body_validator(chunk)
            parser.data_received(chunk)

        return file_name + file_extension

    except ClientDisconnect:
        print("Client Disconnected")
    except MaxBodySizeException as e:
        raise HTTPException(status_code=413,
                            detail=f'Maximum request body size limit ({config["max_file_size"]} bytes) exceeded ({e.body_len} bytes read)')
    except streaming_form_data.validators.ValidationError:
        raise HTTPException(status_code=413,
                            detail=f'Maximum file size limit ({config["max_file_size"]} bytes) exceeded')
    except Exception:
        raise HTTPException(status_code=500,
                            detail='There was an error uploading the file')

    if not file_.multipart_filename:
        raise HTTPException(status_code=422, detail='File is missing')



@app.post("/", response_class=PlainTextResponse)
async def post_file(request: Request, api_key: str = Depends(check_api_key)):
    file_name = await process_file(request)


    # Return the URL of the uploaded file
    return f"{url}{file_name}"


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
                log_level=config["log_level"],
                )