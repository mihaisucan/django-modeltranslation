# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy


class TestModel(models.Model):
    title = models.CharField(ugettext_lazy('title'), max_length=255)
    text = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)


class TestModelFallback(models.Model):
    title = models.CharField(ugettext_lazy('title'), max_length=255)
    text = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)


class TestModelFallback2(models.Model):
    title = models.CharField(ugettext_lazy('title'), max_length=255)
    text = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)


class TestModelFileFields(models.Model):
    title = models.CharField(ugettext_lazy('title'), max_length=255)
    file = models.FileField(upload_to='test', null=True, blank=True)
    image = models.ImageField(upload_to='test', null=True, blank=True)


class TestModelMultitableA(models.Model):
    titlea = models.CharField(ugettext_lazy('title a'), max_length=255)


class TestModelMultitableB(TestModelMultitableA):
    titleb = models.CharField(ugettext_lazy('title b'), max_length=255)


class TestModelMultitableC(TestModelMultitableB):
    titlec = models.CharField(ugettext_lazy('title c'), max_length=255)


class TestModelMultitableD(TestModelMultitableB):
    titled = models.CharField(ugettext_lazy('title d'), max_length=255)


class TestModelAbstractA(models.Model):
    titlea = models.CharField(ugettext_lazy('title a'), max_length=255)

    class Meta:
        abstract = True


class TestModelAbstractB(TestModelAbstractA):
    titleb = models.CharField(ugettext_lazy('title b'), max_length=255)


class DataModel(models.Model):
    data = models.TextField(blank=True, null=True)


class CustomManager(models.Manager):
    def get_query_set(self):
        return super(CustomManager, self).get_query_set().filter(
            name__contains='a')

    def foo(self):
        return 'bar'


class TestModelCustomManager(models.Model):
    name = models.CharField(max_length=50)

    objects = CustomManager()
