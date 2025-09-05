from django.db import models
from simple_history.models import HistoricalRecords


class Product(models.Model):
    name = models.CharField(
        verbose_name="Nome", max_length=200, null=False, blank=False, unique=True
    )


class Store(models.Model):
    name = models.CharField(verbose_name="Nome", max_length=30, null=False, blank=False)
    logo = models.CharField(
        verbose_name="Logo", max_length=200, null=False, blank=False
    )
    url = models.CharField(verbose_name="Link", max_length=100, null=False, blank=False)


class Stock(models.Model):
    price = models.FloatField(verbose_name="Preço", null=False, blank=False)
    is_available = models.BooleanField(null=False, blank=False)
    url = models.CharField(verbose_name="Link", max_length=200, null=False, blank=False)
    photo = models.CharField(
        verbose_name="Foto", max_length=200, null=False, blank=False
    )
    category = models.CharField(
        verbose_name="Categoria", max_length=50, null=False, blank=False
    )
    sub_group = models.CharField(
        verbose_name="Sub-grupo", max_length=50, null=False, blank=False
    )
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    history = HistoricalRecords()
