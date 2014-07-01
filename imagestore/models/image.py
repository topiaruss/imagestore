#!/usr/bin/env python
# vim:fileencoding=utf-8

__author__ = 'zeus'

from django.db import models
from django.utils.translation import ugettext_lazy as _

from bases.image import BaseImage
from thumbnail.models import AsyncThumbnailMixin


class Image(AsyncThumbnailMixin, BaseImage):
    """
    An image for the gallery, with special front-end behaviour when the video URL is populated.

    """
    image_field_name = 'image'

    class Meta(BaseImage.Meta):
        abstract = False
        verbose_name = _('Image')
        verbose_name_plural = _('Images')
        app_label = 'imagestore'

    video_url = models.URLField(
        _('Video URL'), default='', blank=True,
        help_text=_(
            'When set, the has_video template tag will be True, and a video player will play this URL.'))

    def has_video(self):
        """
        Use this for the logical testing of whether a video is present.
        """
        return bool(self.video_url)
