# Generated by Django 3.1 on 2020-05-22 22:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_auto_20200523_0144'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='author',
            options={'ordering': ['last_name']},
        ),
    ]
