# Generated by Django 3.0.7 on 2020-06-25 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_memory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='memory',
            name='type',
            field=models.CharField(max_length=32, verbose_name='类型'),
        ),
    ]