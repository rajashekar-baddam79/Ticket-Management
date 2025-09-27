import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TicketSystem.settings')

app = Celery('TicketSystem')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

#Celery Beat settings for periodic tasks
app.conf.beat_schedule = {
    'check-for-escalations-every-minute': {
        'task': 'user_desk.tasks.check_for_escalations',
        'schedule': 6000.0,  # Run every 60 seconds (1 minute)
        'args': (),
    },
}