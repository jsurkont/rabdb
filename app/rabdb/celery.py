from __future__ import absolute_import, unicode_literals
import os
from celery import Celery


# set the default Django settings module for the 'celery' program.
# if os.environ.get('RABDB_ENV') == 'production':
#     os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rabdb.settings_production')
# else:
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rabdb.settings')

app = Celery('rabdb')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
# if os.environ.get('RABDB_ENV') == 'production':
#     app.config_from_object('django.conf:settings_production', namespace='CELERY')
# else:
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
