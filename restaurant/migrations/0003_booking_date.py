# Generated by Django 4.2 on 2023-04-25 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0002_menu_menu_item_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='date',
            field=models.DateField(default=None),
            preserve_default=False,
        ),
    ]
