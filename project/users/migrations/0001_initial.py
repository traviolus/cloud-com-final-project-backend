# Generated by Django 3.2 on 2021-04-13 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(db_index=True, max_length=255)),
                ('last_name', models.CharField(db_index=True, max_length=255)),
                ('employee_id', models.IntegerField()),
                ('credit', models.IntegerField(default=100)),
            ],
        ),
    ]
