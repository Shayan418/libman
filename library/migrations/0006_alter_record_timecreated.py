# Generated by Django 4.0.1 on 2022-02-10 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0005_alter_record_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='timeCreated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]