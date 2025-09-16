# master_db/apps.py
from django.apps import AppConfig

class MasterDbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'master_db'
