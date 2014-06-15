#!/usr/bin/env python
# vim:fileencoding=utf-8
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

__author__ = 'zeus'

import exifread
import logging
import zipfile
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.files.base import ContentFile
from tagging_autocomplete.models import TagAutocompleteField
from django.core.files.storage import default_storage

try:
    import Image as PILImage
except ImportError:
    from PIL import Image as PILImage

from imagestore.models import Album, Image

logger = logging.getLogger(__name__)

TEMP_DIR = getattr(settings, 'TEMP_DIR', 'temp/')

def timing(msg):
    logger.debug(msg)

def process_zipfile(uploaded_album):

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

    timing("checking uploaded album exists")
    if default_storage.exists(uploaded_album.zip_file.name):
        # TODO: implement try-except here
        timing("build the zipfile reference")
        zip = zipfile.ZipFile(uploaded_album.zip_file)
        timing("test the zipfile")
        bad_file = zip.testzip()
        if bad_file:
            raise Exception('"%s" in the .zip archive is corrupt.' % bad_file)

        if not uploaded_album.album:
            uploaded_album.album = Album.objects.create(name=uploaded_album.new_album_name)

        from cStringIO import StringIO
        for filename in sorted(zip.namelist()):
            if filename.startswith('__'):  # do not process meta files
                continue

            fname = filename.encode('ascii', errors='replace')
            timing('looping for %s' % fname)
            print fname

            timing('read the individual file')
            data = zip.read(filename)
            if len(data):
                timing('determined it has content')
                try:
                    # the following is taken from django.forms.fields.ImageField:
                    # load() could spot a truncated JPEG, but it loads the entire
                    # image in memory, which is a DoS vector. See #3848 and #18520.
                    # verify() must be called immediately after the constructor.
                    timing('verifying')
                    PILImage.open(StringIO(data)).verify()
                    timing('verified')
                except Exception, ex:
                    # if a "bad" file is found we just skip it.
                    logger.error('Error while verifying image: %s' % ex.message)
                    continue

                if hasattr(data, 'seek') and callable(data.seek):
                    data.seek(0)
                    timing('seeked start of file')
                exif = exifread.process_file(StringIO(data))
                timing('exif extraction done')
                xif = flatten_exif(exif)
                if hasattr(data, 'seek') and callable(data.seek):
                    print 'seeked'
                    data.seek(0)
                    timing('seeked start of file, again')

                try:
                    img = Image(album=uploaded_album.album,
                                tags=uploaded_album._tags_cache,
                                event_name=uploaded_album.event_name,
                                photographers_name=uploaded_album.photographers_name,
                                photo_date=uploaded_album.photo_date,
                                description=uploaded_album.image_description,
                                exif=xif,
                                )
                    img.image.save(filename, ContentFile(data))
                    img.save()
                    timing('saved image')
                except Exception, ex:
                    logger.error('error creating Image: %s' % ex.message)
        zip.close()
        timing('closed zip file')
        uploaded_album.delete()


upload_processor_function = getattr(settings, 'IMAGESTORE_UPLOAD_ALBUM_PROCESSOR', None)
upload_processor = process_zipfile
if upload_processor_function:
    i = upload_processor_function.rfind('.')
    module, attr = upload_processor_function[:i], upload_processor_function[i+1:]
    try:
        mod = import_module(module)
    except ImportError as e:
        raise ImproperlyConfigured('Error importing request processor module %s: "%s"' % (module, e))
    try:
        upload_processor = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" callable request processor' % (module, attr))


class AlbumUpload(models.Model):
    """
    Just re-written django-photologue GalleryUpload method
    """
    zip_file = models.FileField(_('images file (.zip)'), upload_to=TEMP_DIR,
                                help_text=_('Select a .zip file of images to upload into a new Gallery.'))
    album = models.ForeignKey(
        Album,
        null=True,
        blank=True,
        help_text=_('Select an album to add these images to. leave this empty to create a new album from the supplied title.')
    )
    new_album_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('New album name'),
        help_text=_('If not empty, a new album with this name will be created and images will be upload to this album')
        )
    photographers_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Photographer's name"),
        help_text=_('Will be added to each uploaded image')
        )
    event_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Event name"),
        help_text=_('Will be added to each uploaded image')
        )
    image_description = models.TextField(
        max_length=100,
        blank=True,
        verbose_name=_("Image description"),
        help_text=_('Will be added to each uploaded image')
        )
    photo_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Date override"),
        help_text=_('This will override the internal EXIF date of each uploaded image')
        )
    tags = TagAutocompleteField(
        help_text=_('Comma separated. These will be added to each uploaded image')
        )

    class Meta(object):
        verbose_name = _('Album upload')
        verbose_name_plural = _('Album uploads')
        app_label = 'imagestore'

    def save(self, *args, **kwargs):
        timing('uploading via superclass')
        super(AlbumUpload, self).save(*args, **kwargs)
        timing('invoking upload_processor')
        upload_processor(self)

    def delete(self, *args, **kwargs):
        storage, path = self.zip_file.storage, self.zip_file.name
        super(AlbumUpload, self).delete(*args, **kwargs)
        storage.delete(path)
