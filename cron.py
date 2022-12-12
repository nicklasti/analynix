import django
from django.conf import settings
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "analynix.settings"

django.setup()

cron_jobs = settings.CRONJOBS

user = 'analynix'

for cron_job in cron_jobs:
    schedule, command = cron_job
    os.system(f"crontab -e u {user}")
    os.system(f"{schedule} {command}")
    #os.system("usr/bin/python /analynix/scripts/secondscript.py")