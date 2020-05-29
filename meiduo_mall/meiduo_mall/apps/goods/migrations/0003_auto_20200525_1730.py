# Generated by Django 2.2.5 on 2020-05-25 17:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0002_goodsvisitcount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goodsspecification',
            name='goods',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specs', to='goods.Goods', verbose_name='商品'),
        ),
        migrations.AlterField(
            model_name='skuspecification',
            name='sku',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specs', to='goods.SKU', verbose_name='sku'),
        ),
        migrations.AlterField(
            model_name='specificationoption',
            name='spec',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='goods.GoodsSpecification', verbose_name='规格'),
        ),
    ]