# Generated by Django 3.2 on 2021-04-25 12:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20210425_1225'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='facebook_id',
            field=models.BigIntegerField(null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
