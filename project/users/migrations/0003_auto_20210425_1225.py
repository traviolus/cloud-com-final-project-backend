# Generated by Django 3.2 on 2021-04-25 12:25

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_employee_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='current_state',
            field=models.CharField(choices=[('NON_REGIS', 'Not Registered'), ('PROMPT_REGIS', 'Prompt Register'), ('VERIFYING', 'Verifying'), ('IDLE', 'Idle'), ('PROMPT_PRINT', 'Prompt Print'), ('QUEUE', 'Queue'), ('PRINTING', 'Printing')], default='NON_REGIS', max_length=12),
        ),
        migrations.AlterField(
            model_name='user',
            name='employee_id',
            field=models.BigIntegerField(validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
