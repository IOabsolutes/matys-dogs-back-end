# Generated by Django 4.2.8 on 2024-01-21 15:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dog_card', '0004_alter_dogcardmodel_photo'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dogcardmodel',
            options={'ordering': ['id']},
        ),
    ]
