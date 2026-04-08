from celery import Celery
from app.core.config import settings
#xử lý tác vụ nền và không blocking API
celery_app = Celery(
    "worker",
    #nhận task từ backend, đưa vào queue, phân phối cho worker xử lý
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# autodiscover tasks in app.services.tasks
celery_app.autodiscover_tasks(["app.services.tasks"])