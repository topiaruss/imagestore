#!/usr/bin/env python
# vim:fileencoding=utf-8

__author__ = 'zeus'

import datetime
import logging
import exifread

from django.db import models
from django.db.models import permalink
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
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

    title = models.CharField(_('Title'), max_length=100, blank=True,
                             help_text=_("The image title."))

    description = models.TextField(
        max_length=100,
        blank=True,
        verbose_name=_("Image description"),
        help_text=_("A description for the image"),
    )

    tags = TagAutocompleteField(
        help_text=_(
            "Start typing a tag, and suggestions will be made. Multiple tags are possible. For spaces, comma separate.")
    )

    order = models.IntegerField(
        _('Order'), default=0,
        help_text=_(
            "Used when displaying in the standard imagestore Album, not in the imagesift gallery."),
    )

    image = ImageField(
        verbose_name=_('File'), upload_to=get_file_path,
        help_text=_(
            "An image file, possibly containing EXIF data, which may be rendered in a template."),
    )

    user = models.ForeignKey(
        User, verbose_name=_('User'), null=True, blank=True, related_name='images',
        help_text=_("Currently not used. Deprecated."),
    )
    created = models.DateTimeField(_('Created'), auto_now_add=True, null=True)
    updated = models.DateTimeField(_('Updated'), auto_now=True, null=True)
    album = models.ForeignKey(get_model_string('Album'), verbose_name=_('Album'), null=True, blank=True,
                              related_name='images',
                              help_text=_("The album this image belongs to. Images may be outside of an album."),
    )

    photographers_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Photographer's name"),
        help_text=_(
            'This name overrides the content of the Artist and Copyright fields if there is any EXIF data.'),
    )

    event_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Event name"),
        help_text=_('Used for display only.'),
    )

    photo_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Date override"),
        help_text=_("This will override the image's EXIF date and time")
    )

    exif = JsonField(
        null=True, blank=True,
        help_text=_(
            "This EXIF data was extracted and stored when the image was uploaded. Best not to edit it."))

    def save(self, *args, **kwargs):
        """
        override save so that we can grab the exif data on the image.
        TODO: optimise so that we only fetch exif data when the image is first saved, or updated.
        """
        def flatten_exif(exif):
            xif = {}
            for k, v in exif.items():
                try:
                    if k == 'JPEGThumbnail':
                        continue
                    xif.update({k:v.printable})
                except AttributeError, ex:
                    logger.exception('%s in k, v: %s :: %s' % (ex, k, v))
            return xif
        ff = self.image.storage.open(self.image.name)
        exif = exifread.process_file(ff)
        xif = flatten_exif(exif)
        self.exif=xif
        super(BaseImage, self).save(*args, **kwargs)

    @permalink
    def get_absolute_url(self):
        return 'imagestore:image', (), {'pk': self.id}

    def __unicode__(self):
        return '%s' % self.id

    def overrideable_date(self):
        """
        Return the override date, or the EXIF date, or the created date
        """
        if self.photo_date:
            return self.photo_date
        exif_date = self.raw_exif_datetime()
        if exif_date is not None:
            return exif_date
        # perhaps we should get the original image file date?
        return self.created

    overrideable_date.short_description = _('Raw Exif Datetime')

    def overrideable_photographer(self):
        """
        Guessing the best behaviour here.
        If photographer defined, return it.
        Else, if EXIF artist defined, return it.
        Else, if Copyright defined, return it.
        Else, return empty.
        """
        if self.photographers_name:
            return self.photographers_name

        try:
            artist = self.exif_by_block()['Image']['Artist']
            if artist:
                return artist
        except KeyError:
            pass

        try:
            copyright = self.exif_by_block()['Image']['Copyright']
            if copyright:
                return copyright
        except KeyError:
            pass

        return ''

    def raw_exif_datetime(self):
        """
        Get the raw EXIF date with TZ, returning None if on a KeyError or parsing problem
        """
        try:
            exifdate = self.exif['Image DateTime']
            dt = datetime.datetime.strptime(exifdate, '%Y:%m:%d %H:%M:%S')
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt, timezone.get_current_timezone())
            return dt
        except Exception, ex:
            logger.exception("handled exception in raw_exif_datetime. No sweat.")
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

    def pprint_object(self, obj):
        """
        Handy for documenting exif_by_block ret value
        """
        import pprint
        pprint.PrettyPrinter(indent=4).pprint(obj)

    def exif_by_block(self):
        """
        Splits the EXIF data into blocks, for easy access in templates:
            {{ image.exif_by_block.GPS.GPSLatitude }}
            {{ image.exif_by_block.EXIF.ApertureValue }}
            {{ image.exif_by_block.Image.Copyright }}

        Below is an example of the ret value, for a specific image::

        {
            u'EXIF': {u'ApertureValue': u'53/8',
                      u'ColorSpace': u'sRGB',
                      u'ComponentsConfiguration': u'YCbCr',
                      u'CustomRendered': u'Normal',
                      u'DateTimeDigitized': u'2009:09:12 14:42:56',
                      u'DateTimeOriginal': u'2009:09:12 14:42:56',
                      u'ExifImageLength': u'320',
                      u'ExifImageWidth': u'213',
                      u'ExifVersion': u'0221',
                      u'ExposureBiasValue': u'0',
                      u'ExposureMode': u'Auto Exposure',
                      u'ExposureProgram': u'Program Normal',
                      u'ExposureTime': u'1/500',
                      u'FNumber': u'10',
                      u'Flash': u'Flash did not fire, compulsory flash mode',
                      u'FlashPixVersion': u'0100',
                      u'FocalLength': u'38',
                      u'FocalPlaneResolutionUnit': u'2',
                      u'FocalPlaneXResolution': u'207302/39',
                      u'FocalPlaneYResolution': u'245747/46',
                      u'ISOSpeedRatings': u'800',
                      u'MaxApertureValue': u'3363/1189',
                      u'MeteringMode': u'Spot',
                      u'SceneCaptureType': u'Standard',
                      u'ShutterSpeedValue': u'9',
                      u'SubSecTime': u'11',
                      u'SubSecTimeDigitized': u'11',
                      u'SubSecTimeOriginal': u'11',
                      u'UserComment': u' ',
                      u'WhiteBalance': u'Auto'},
            u'GPS': {u'GPSDate': u'2009:09:12',
                     u'GPSLatitude': u'[35, 16, 4887/100]',
                     u'GPSLatitudeRef': u'N',
                     u'GPSLongitude': u'[120, 39, 2661/50]',
                     u'GPSLongitudeRef': u'W',
                     u'GPSTimeStamp': u'[21, 42, 56]',
                     u'GPSVersionID': u'[2, 2, 0, 0]'},
            u'Image': {u'Artist': u'Russ Ferriday',
                       u'Copyright': u'Copyright: Russell Ferriday',
                       u'DateTime': u'2009:09:12 14:42:56',
                       u'ExifOffset': u'288',
                       u'GPSInfo': u'776',
                       u'ImageDescription': u' ',
                       u'Make': u'Canon',
                       u'Model': u'Canon EOS REBEL T1i',
                       u'Orientation': u'Horizontal (normal)',
                       u'ResolutionUnit': u'Pixels/Inch',
                       u'Software': u'iPhoto 9.4.3',
                       u'XResolution': u'72',
                       u'YResolution': u'72'}}


        """
        if self.exif is None:
            return {}
        if hasattr(self, '_cached_exif_by_block'):
            return self._cached_exif_by_block
        ret = {}
        for k, v in self.exif.items():
            try:
                block, key = k.split()
                ret.setdefault(block, {})[key] = v
            except Exception, ex:
                logger.exception("in exif_by_block k is %s, msg is %s" % (k, ex.message))
        self._cached_exif_by_block = ret
        # self.pprint_object(ret)  #  just for creating doc/exploring
        return ret


# noinspection PyUnusedLocal
def setup_imagestore_permissions(instance, created, **kwargs):
    if not created:
        return
    try:
        from imagestore.models import Album, Image

        album_type = ContentType.objects.get(
            #app_label=load_class('imagestore.models.Album')._meta.app_label,
            app_label=Album._meta.app_label,
            name='Album'
        )
        image_type = ContentType.objects.get(
            #app_label=load_class('imagestore.models.Image')._meta.app_label,
            app_label=Image._meta.app_label,
            name='Image'
        )
        add_image_permission = Permission.objects.get(codename='add_image', content_type=image_type)
        add_album_permission = Permission.objects.get(codename='add_album', content_type=album_type)
        change_image_permission = Permission.objects.get(codename='change_image', content_type=image_type)
        change_album_permission = Permission.objects.get(codename='change_album', content_type=album_type)
        delete_image_permission = Permission.objects.get(codename='delete_image', content_type=image_type)
        delete_album_permission = Permission.objects.get(codename='delete_album', content_type=album_type)
        instance.user_permissions.add(add_image_permission, add_album_permission, )
        instance.user_permissions.add(change_image_permission, change_album_permission, )
        instance.user_permissions.add(delete_image_permission, delete_album_permission, )
    except ObjectDoesNotExist:
        # Permissions are not yet installed or content not created yet
        # probably this is first
        logger.exception('handled exception in setup_imagestore_permissions')
        pass


if SELF_MANAGE:
    post_save.connect(setup_imagestore_permissions, User)
