# Generated by Django 5.1.6 on 2025-02-16 07:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pdf_tools', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uploadedpdf',
            name='uploaded_at',
        ),
    ]
