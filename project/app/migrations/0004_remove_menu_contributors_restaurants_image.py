# Generated by Django 4.2 on 2023-05-09 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_remove_restaurants_reviews_restaurants_description_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='menu',
            name='contributors',
        ),
        migrations.AddField(
            model_name='restaurants',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]
