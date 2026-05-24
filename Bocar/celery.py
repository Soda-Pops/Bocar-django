import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Bocar.settings')

app = Celery('Bocar')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
