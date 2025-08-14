from celery import Celery

from app.core.config import settings

app = Celery(
    "digitalhuman_celery",
    broker=settings.celery_broker_url,
    backend=settings.celery_backend_url,
)


# celery配置前缀应为: `CELERY_`
# app.config_from_object(settings, namespace="CELERY")
app.conf.result_extended = True  # 保存任务的参数到backends中

# 加载任务
app.autodiscover_tasks(
    [
        "app.tasks.reviews",
        "app.tasks.audit",
    ]
)
