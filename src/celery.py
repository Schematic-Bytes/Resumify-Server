from celery import Celery
from src.config import REDIS_URL

app = Celery(
    backend=f"{REDIS_URL}/2",
    broker=f"{REDIS_URL}/3",
)

app.conf.task_serializer = 'pickle'
app.autodiscover_tasks(['src.tasks'])
app.conf.accept_content = ['pickle']
