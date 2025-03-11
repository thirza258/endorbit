# Generated by Django 5.1.6 on 2025-03-10 15:12

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("product_url", models.URLField(blank=True, null=True)),
                (
                    "product_name",
                    models.CharField(blank=True, max_length=200, null=True),
                ),
                (
                    "retail_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                ("image", models.URLField(blank=True, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "product_rating",
                    models.DecimalField(
                        blank=True, decimal_places=1, max_digits=2, null=True
                    ),
                ),
                ("brand", models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
    ]
