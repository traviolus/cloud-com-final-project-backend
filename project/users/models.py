from django.db import models
from django.core.validators import MinValueValidator


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255, db_index=True)
    last_name = models.CharField(max_length=255, db_index=True)
    employee_id = models.BigIntegerField(validators=[MinValueValidator(0)])
    credit = models.IntegerField(default=100)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    