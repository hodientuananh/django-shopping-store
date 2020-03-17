# Generated by Django 2.2.8 on 2020-03-17 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20200317_0728'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='category',
            field=models.CharField(choices=[('TS', 'T-Shirt'), ('SW', 'Sport Wear'), ('OW', 'Out Wear')], default='TS', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='item',
            name='label',
            field=models.CharField(choices=[('P', 'primary'), ('S', 'secondary'), ('D', 'danger')], default='P', max_length=100),
            preserve_default=False,
        ),
    ]