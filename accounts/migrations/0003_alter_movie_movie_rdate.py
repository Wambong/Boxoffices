# Generated by Django 4.1.3 on 2023-08-30 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_movie_movie_rdate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='movie_rdate',
            field=models.CharField(default='null', max_length=20),
        ),
    ]
