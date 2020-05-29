# Generated by Django 2.2.5 on 2020-05-28 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0005_auto_20200527_2012'),
    ]

    operations = [
        migrations.AddField(
            model_name='goods',
            name='desc_detail',
            field=models.TextField(default='', verbose_name='详细介绍'),
        ),
        migrations.AddField(
            model_name='goods',
            name='desc_pack',
            field=models.TextField(default='', verbose_name='包装信息'),
        ),
        migrations.AddField(
            model_name='goods',
            name='desc_service',
            field=models.TextField(default='', verbose_name='售后服务'),
        ),
    ]
