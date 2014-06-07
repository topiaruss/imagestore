#!/usr/bin/env python
# vim:fileencoding=utf-8

__author__ = 'zeus'

import datetime
import logging

from django.db import models
from django.db.models import permalink
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Permission
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from sorl.thumbnail.helpers import ThumbnailError
from tagging_autocomplete.models import TagAutocompleteField
from django_pgjson.fields import JsonField
from sorl.thumbnail import ImageField, get_thumbnail


logger = logging.getLogger(__name__)


try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User

try:
    import Image as PILImage
except ImportError:
    from PIL import Image as PILImage

from imagestore.utils import get_file_path, get_model_string

SELF_MANAGE = getattr(settings, 'IMAGESTORE_SELF_MANAGE', True)


class BaseImage(models.Model):
    class Meta(object):
        abstract = True
        ordering = ('order', 'id')
        permissions = (
            ('moderate_images', 'View, update and delete any image'),
        )

    title = models.CharField(_('Title'), max_length=100, blank=True, null=True)
    description = models.TextField(
        max_length=100,
        blank=True,
        verbose_name=_("Image description"),
        )
    tags = TagAutocompleteField()

    order = models.IntegerField(_('Order'), default=0)
    image = ImageField(verbose_name = _('File'), upload_to=get_file_path)
    user = models.ForeignKey(User, verbose_name=_('User'), null=True, blank=True, related_name='images')
    created = models.DateTimeField(_('Created'), auto_now_add=True, null=True)
    updated = models.DateTimeField(_('Updated'), auto_now=True, null=True)
    album = models.ForeignKey(get_model_string('Album'), verbose_name=_('Album'), null=True, blank=True, related_name='images')

    photographers_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Photographer's name"),
        )
    event_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Event name"),
        )
    photo_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Date override"),
        help_text=_("This will override the image's EXIF date")
        )
    exif = JsonField(null=True, blank=True)

    @permalink
    def get_absolute_url(self):
        return 'imagestore:image', (), {'pk': self.id}


    def overrideable_date(self):
        """
        Get the exif date, but override if the photo_date is set
        """
        if self.photo_date:
            return self.photo_data
        return self.raw_exif_datetime()
    overrideable_date.short_description = _('Raw Exif Datetime')

    def __unicode__(self):
        return '%s'% self.id

    def raw_exif_datetime(self):
        try:
            exifdate = self.exif['Image DateTime']
            dt = datetime.datetime.strptime(exifdate, '%Y:%m:%d %H:%M:%S')
            return dt
        except Exception, ex:
            logger.exception("raw_exif_datetime")
            return None
    raw_exif_datetime.short_description = _('Raw Exif Datetime')

    def admin_thumbnail(self):
        try:
            return '<img src="%s">' % get_thumbnail(self.image, '100x100', crop='center').url
        except IOError:
            logger.exception('IOError for image %s', self.image)
            return 'IOError logged'
        except ThumbnailError, ex:
            return 'ThumbnailError, %s' % ex.message

    admin_thumbnail.short_description = _('Thumbnail')
    admin_thumbnail.allow_tags = True

    # def exifbyblock(self, block):
    #     import pdb; pdb.set_trace()
    #     block = [i for i in self.exif.items() if i[0].startswith(block)]
    #     ret = {}
    #     for k,v in block:
    #         ret[k] = v
    #     return ret

#noinspection PyUnusedLocal
def setup_imagestore_permissions(instance, created, **kwargs):
        if not created:
            return
        try:
            from imagestore.models import Album, Image
            album_type = ContentType.objects.get(
                #app_label=load_class('imagestore.models.Album')._meta.app_label,
                app_label = Album._meta.app_label,
                name='Album'
            )
            image_type = ContentType.objects.get(
                #app_label=load_class('imagestore.models.Image')._meta.app_label,
                app_label = Image._meta.app_label,
                name='Image'
            )
            add_image_permission = Permission.objects.get(codename='add_image', content_type=image_type)
            add_album_permission = Permission.objects.get(codename='add_album', content_type=album_type)
            change_image_permission = Permission.objects.get(codename='change_image', content_type=image_type)
            change_album_permission = Permission.objects.get(codename='change_album', content_type=album_type)
            delete_image_permission = Permission.objects.get(codename='delete_image', content_type=image_type)
            delete_album_permission = Permission.objects.get(codename='delete_album', content_type=album_type)
            instance.user_permissions.add(add_image_permission, add_album_permission,)
            instance.user_permissions.add(change_image_permission, change_album_permission,)
            instance.user_permissions.add(delete_image_permission, delete_album_permission,)
        except ObjectDoesNotExist:
            # Permissions are not yet installed or conten does not created yet
            # probaly this is first
            pass


if SELF_MANAGE:
    post_save.connect(setup_imagestore_permissions, User)
