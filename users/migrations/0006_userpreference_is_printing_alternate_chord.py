# Generated by Django 5.1.2 on 2025-01-22 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_userpreference_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpreference',
            name='is_printing_alternate_chord',
            field=models.BooleanField(default=False),
        ),
    ]
