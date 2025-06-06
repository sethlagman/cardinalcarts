# Generated by Django 5.2 on 2025-04-15 17:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_alter_orderactionlog_order'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductActionLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=255)),
                ('action', models.CharField(choices=[('add', 'Add'), ('edit', 'Edit'), ('delete', 'Delete')], max_length=10)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('admin', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
