# Generated by Django 2.2.5 on 2020-05-27 20:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0003_auto_20200525_1730'),
    ]

    operations = [
        migrations.RenameField(
            model_name='goodsspecification',
            old_name='goods',
            new_name='spu',
        ),
    ]
