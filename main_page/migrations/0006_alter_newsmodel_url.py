# Generated by Django 4.2.8 on 2024-02-07 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_page', '0005_alter_newsmodel_photo_alter_newsmodel_sub_text_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsmodel',
            name='url',
            field=models.URLField(max_length=300),
        ),
    ]