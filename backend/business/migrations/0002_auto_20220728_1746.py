# Generated by Django 2.2.28 on 2022-07-28 17:46

import business.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='business',
            name='profile_image',
            field=models.FileField(blank=True, null=True, upload_to=business.models.business_directory_path, verbose_name='Profile Picture'),
        ),
        migrations.AlterField(
            model_name='businessaddress',
            name='business',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='business.Business'),
        ),
    ]
