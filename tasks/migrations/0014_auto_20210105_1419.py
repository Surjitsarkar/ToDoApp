# Generated by Django 3.1.4 on 2021-01-05 08:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0013_auto_20210105_1233'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['-date_created']},
        ),
    ]
