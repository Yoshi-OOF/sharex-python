import os
import random
import string


def name_gen(filename: str, folder: str, size) -> (str, str):
    file_extension = os.path.splitext(filename)[1]
    file_name = ''.join(
        random.choices(
            string.ascii_letters + string.digits,
            k=size
        )
    )

    return f"{folder}/{file_name}{file_extension}", f'{file_name}{file_extension}'


def cancel_upload(path: str):
    if os.path.exists(path):
        os.remove(path)

