# Generated by Django 5.1.4 on 2025-01-11 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autenticad', '0005_media_folder_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='file_path',
            field=models.ImageField(upload_to='media_files/ , max_length=255'),
        ),
    ]
