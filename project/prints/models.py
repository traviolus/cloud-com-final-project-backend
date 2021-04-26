from django.db import models
from users.models import User


def user_directory_path(instance, filename):
    return f'user_{instance.owner.user_id}/{filename}'


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
    document = models.FileField(upload_to=user_directory_path)
    status = models.IntegerField(choices=STATUS_CHOICES, default=QUEUING)

    def __str__(self):
        return f'{self.task_id}: {self.owner} [{self.get_status_display()}]'
