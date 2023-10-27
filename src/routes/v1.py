import json
from shutil import copyfileobj
from uuid import uuid4

from fastapi import FastAPI, File, UploadFile, status
from fastapi.responses import JSONResponse

from src.config import OPENAI_API_KEY, TMP_DIRECTORY, logger, redis
from src.parse_lib import ResumeParser
from src.tasks.job import queue_multiple_files


def single_search(file: UploadFile):
    if file.content_type != "application/pdf":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'status': "error", "message": "Only PDF files are supported"},
        )
    try:
        response = ResumeParser(OPENAI_API_KEY).query_resume(pdf_file=file.file)
        logger.info(f"Response for {file.filename} is completed")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={'status': "success", "data": response},
        )
    except Exception as e:
        logger.error(f"Response for {file.filename} failed\n{e}", exc_info=1, stack_info=True)
        return JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content={'status': "error", "message": "We are unable to parse this resume."},
        )


def get_queued_job(_id: str):
    if redis.exists((_key := f'result:{_id}')):
        logger.info(f"Query successfull ({_id})")
        mapping = redis.hgetall(_key)
        parsed_mapping = {k: json.loads(v) for k, v in mapping.items()}
        return parsed_mapping
    else:
        logger.info(f"Query job not found ({_id})")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={'status': "success", "message": "Job not completed"}
        )


def multi_file_parse(files: list[UploadFile]):
    _id = str(uuid4())

    current_tmp_directory = TMP_DIRECTORY / _id
    current_tmp_directory.mkdir(parents=True, exist_ok=True)

    file_name_list = list()
    for file in files:
        if file.content_type != "application/pdf":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    'status': 'error',
                    'message': f'Unsupported file format: {file.filename}. Only PDF files are supported',
                },
            )

        with open(current_tmp_directory / file.filename, 'wb') as fp:
            copyfileobj(file.file, fp)

        file_name_list.append(current_tmp_directory / file.filename)

    queue_multiple_files.delay(files=file_name_list, _id=_id)
    logger.info(f"Job queued for id ({_id})")

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            'status': 'success',
            'data': {
                "id": _id,
            },
        },
    )
