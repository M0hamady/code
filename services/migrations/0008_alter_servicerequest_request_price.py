# Generated by Django 3.2.19 on 2023-06-22 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0007_servicerequest_request_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicerequest',
            name='request_price',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]