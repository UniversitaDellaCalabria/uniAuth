# Generated by Django 3.2.18 on 2023-04-16 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='attributes',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]
