#!/usr/bin/env python
# vim:fileencoding=utf-8

__author__ = 'zeus'

from django.db import models
from django.utils.translation import ugettext_lazy as _

from bases.image import BaseImage
import urlparse
import logging

logger = logging.getLogger(__name__)

class Image(BaseImage):
    """
    An image for the gallery, with special front-end behaviour when the video URL is populated.

    """

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

    @staticmethod
    def is_video_url_legal(url):
        url = url.replace('https://', 'http://')
        return url.startswith('http://www.youtube.com')

    @staticmethod
    def extract_video_token(url):
        return dict(urlparse.parse_qsl(urlparse.urlparse(url).query))['v']

    def video_embed_block(self):
        """
        original url:  https://www.youtube.com/watch?v=BNtrCmFE3OA
        maps to : "<iframe width="480" height="360" src="//www.youtube-nocookie.com/embed/BNtrCmFE3OA?rel=0" frameborder="0" allowfullscreen></iframe>"

        so we let the user put in the original URL.

        We then fish out the token and dress it up in the frame for return to the designer.

        This gives us options to offer more display options later, without logic in the template

        """
        if not self.has_video():
            return u''

        if not self.is_video_url_legal(self.video_url):
            logger.error('Image %s illegal video url %s' % (self.pk, self.video_url))
            return u''

        try:
            token = self.extract_video_token(self.video_url)
        except:
            logger.error('Image %s gives problem extracting vid token %s' % (self.pk, self.video_url))
            return u''

        template = """<iframe width="480" height="360" src="//www.youtube-nocookie.com/embed/{token}?rel=0" frameborder="0" allowfullscreen></iframe>"""
        return template.format(token=token)
