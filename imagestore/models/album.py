#!/usr/bin/env python
# vim:fileencoding=utf-8

__author__ = 'zeus'

from bases.album import BaseAlbum
from django.utils.translation import ugettext_lazy as _
from imagestore.utils import get_model_string

class Album(BaseAlbum):

    class Meta(BaseAlbum.Meta):
        abstract = False
        verbose_name = _('Album')
        verbose_name_plural = _('Albums')
        app_label = 'imagestore'

    head = models.ForeignKey(get_model_string('Image'), related_name='head_of', null=True, blank=True, on_delete=models.SET_NULL)
