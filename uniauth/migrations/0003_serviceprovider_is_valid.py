# Generated by Django 2.2.2 on 2019-07-02 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uniauth', '0002_agreementrecord_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceprovider',
            name='is_valid',
            field=models.BooleanField(default=False),
        ),
    ]