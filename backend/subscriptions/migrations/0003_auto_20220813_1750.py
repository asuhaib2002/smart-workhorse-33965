# Generated by Django 3.2 on 2022-08-13 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0002_alter_subscriptionplan_period'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userssubscription',
            name='date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userssubscription',
            name='expiry',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
