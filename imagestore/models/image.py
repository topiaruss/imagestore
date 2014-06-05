#!/usr/bin/env python
# vim:fileencoding=utf-8

__author__ = 'zeus'

from bases.image import BaseImage
from django.utils.translation import ugettext_lazy as _
from imagestore.utils import get_model_string

class Image(BaseImage):
    class Meta(BaseImage.Meta):
        abstract = False
        verbose_name = _('Image')
        verbose_name_plural = _('Images')
        app_label = 'imagestore'

    album = models.ForeignKey(get_model_string('Album'), verbose_name=_('Album'), null=True, blank=True, related_name='images')
