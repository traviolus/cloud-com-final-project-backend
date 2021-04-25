from django.db import models
from django.core.validators import MinValueValidator


class User(models.Model):
    STATE_CHOICES = [
        ('NON_REGIS', 'Not Registered'),
        ('PROMPT_REGIS', 'Prompt Register'),
        ('IDLE', 'Idle'),
        ('PROMPT_PRINT', 'Prompt Print'),
        ('QUEUEING', 'Queueing'),
        ('PRINTING', 'Printing')
    ]

    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255, db_index=True)
    last_name = models.CharField(max_length=255, db_index=True)
    employee_id = models.BigIntegerField(validators=[MinValueValidator(0)])
    credit = models.IntegerField(default=100)
    current_state = models.CharField(choices=STATE_CHOICES, default='NON_REGIS', max_length=12)
    facebook_id = models.BigIntegerField(validators=[MinValueValidator(0)], null=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    