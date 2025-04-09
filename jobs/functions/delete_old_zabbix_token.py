from datetime import timedelta

from django.utils import timezone
from django_cron import CronJobBase, Schedule

from zabbixproxy.models import ZabbixAuthToken


class DeleteOldTokensCronJob(CronJobBase):
    schedule = Schedule(run_every_mins=60)
    code = "jobs.delete_old_zabbix_tokens_cron_job"

    def do(self):
        now = timezone.now()
        ZabbixAuthToken.objects.filter(created_at__lt=now - timedelta(hours=24)).delete()
