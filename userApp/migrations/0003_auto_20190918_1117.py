# Generated by Django 2.2.5 on 2019-09-18 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userApp', '0002_auto_20190918_1058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='subTime',
            field=models.TimeField(default='00:00'),
        ),
    ]