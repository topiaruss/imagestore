#!/usr/bin/env python
# vim:fileencoding=utf-8

__author__ = 'zeus'

from django.db import models
from django.utils.translation import ugettext_lazy as _

from bases.album import BaseAlbum


class Album(BaseAlbum):

    class Meta(BaseAlbum.Meta):
        abstract = False
        verbose_name = _('Album')
        verbose_name_plural = _('Albums')
        app_label = 'imagestore'

    head = models.ForeignKey('imagesift.Image', related_name='head_of', null=True, blank=True, on_delete=models.SET_NULL)
