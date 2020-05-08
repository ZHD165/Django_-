#!/home/ubuntu/.virtualenvs/meiduo_mall/bin/python
import sys
sys.path.insert(0, '../../')

sys.path.insert(0, '../apps')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mall.settings.dev')

import django
django.setup()

from celery_tasks.html.tasks import generate_static_sku_detail_html
from goods.models import SKU



skus = SKU.objects.all()
for sku in skus:
    generate_static_sku_detail_html.delay(sku.id)
