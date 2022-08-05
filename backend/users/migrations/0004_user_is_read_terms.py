# Generated by Django 3.2 on 2022-08-05 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_first_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_read_terms',
            field=models.BooleanField(default=False, verbose_name='Is Terms and Condition Read?'),
        ),
    ]
