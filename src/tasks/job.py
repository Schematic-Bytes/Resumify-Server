import json
from pathlib import Path

from src.celery import app
from src.config import OPENAI_API_KEY, logger, redis
from src.parse_lib import ResumeParser

print("App Registered")


@app.task
def queue_multiple_files(files: list[Path], _id: str):
    parser = ResumeParser(OPENAI_API_KEY)
    result_dict = {}
    logger.info(f"Proccessing task for id({_id}) files -> ({len(files)})")
    for file in files:
        try:
            response = json.dumps(parser.query_resume(pdf_file=file))
        except Exception as e:
            logger.error(f"Response for {file} failed\n{e}", exc_info=1, stack_info=True)
            response = json.dumps("failed")
        result_dict[file.name] = response
    logger.info(f"Task id({_id}) completed, failed ({len([x for x in result_dict.values() if x == 'failed'])})")

    redis.hmset(f'result:{_id}', result_dict)
