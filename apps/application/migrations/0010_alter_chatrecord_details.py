# Generated by Django 4.2.13 on 2024-07-15 15:52

import application.models.application
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0009_application_type_application_work_flow_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatrecord',
            name='details',
            field=models.JSONField(default=dict, encoder=application.models.application.DateEncoder, verbose_name='对话详情'),
        ),
    ]