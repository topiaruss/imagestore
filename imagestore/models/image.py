#!/usr/bin/env python
# vim:fileencoding=utf-8

__author__ = 'zeus'

from django.db import models
from bases.image import BaseImage
from django.utils.translation import ugettext_lazy as _

# class Image(BaseImage):
#     class Meta(BaseImage.Meta):
#         abstract = False
#         verbose_name = _('Image')
#         verbose_name_plural = _('Images')
#         app_label = 'imagestore'
#
#     album = models.ForeignKey('imagestore.Album', verbose_name=_('Album'), null=True, blank=True, related_name='images')

class Image(BaseImage):
    """
    An image for the gallery, with special front-end behaviour when the video URL is populated.

    """
    class Meta(BaseImage.Meta):
        abstract = False
        verbose_name = _('Image')
        verbose_name_plural = _('Images')
        app_label = 'imagestore'

    video_url = models.URLField(_('Video URL'), default='')

    def has_video(self):
        """
        Use this for the logical testing of whether a video is present.
        """
        return bool(self.video_url)
