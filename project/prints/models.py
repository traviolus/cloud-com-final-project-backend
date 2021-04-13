from django.db import models
from users.models import User


class PrintTask(models.Model):
    QUEUING = 1
    PRINTING = 2
    DONE = 3
    STATUS_CHOICES = [
        (QUEUING, 'Queuing'),
        (PRINTING, 'Printing'),
        (DONE, 'Done')
    ]

    task_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tasks')
    file_url = models.CharField(max_length=255)
    status = models.IntegerField(choices=STATUS_CHOICES, default=QUEUING)

    def __str__(self):
        return f'{self.task_id}: {self.owner} [{self.get_status_display()}]'
