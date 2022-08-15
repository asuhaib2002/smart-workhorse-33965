# Generated by Django 3.2 on 2022-08-13 15:37

from django.db import migrations, models
import subscriptions.enums


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriptionplan',
            name='period',
            field=models.CharField(blank=True, choices=[('MONTHLY', 'MONTHLY'), ('YEARLY', 'YEARLY')], default=subscriptions.enums.SubscriptionPeriod['YEARLY'], max_length=200, null=True),
        ),
    ]
