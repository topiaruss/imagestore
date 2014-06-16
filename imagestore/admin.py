from django.contrib import admin
from imagestore.models import Image, Album, AlbumUpload
from sorl.thumbnail.admin import AdminInlineImageMixin
from django.conf import settings

class InlineImageAdmin(AdminInlineImageMixin, admin.TabularInline):
    model = Image
    fieldsets = (
        (None,
         {'fields': ['title', 'image', 'photographers_name','event_name', 'photo_date', 'tags', 'album',]}
        ),
    )
    raw_id_fields = ('user', )
    extra = 0


class AlbumAdmin(admin.ModelAdmin):
    fieldsets = ((None, {'fields': ['name', 'is_public', 'order']}),)
    list_display = ('name', 'admin_thumbnail', 'user', 'created', 'updated', 'is_public', 'order')
    list_editable = ('order', )
    inlines = [InlineImageAdmin]

admin.site.register(Album, AlbumAdmin)

class ImageAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,
         {'fields': ['title', 'image', 'video_url',
                     'photographers_name','event_name',
                     'photo_date', 'tags', 'album', 'description',
                     'exif',]}
        ),
    )
    list_display = ('admin_thumbnail', 'album', 'title', 'event_name', 'tags', 'photographers_name',
                    'raw_exif_datetime', 'photo_date',  'video_url')
    raw_id_fields = ('user', )
    list_filter = ('album', 'photographers_name', 'event_name')

class AlbumUploadAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        return False

IMAGE_MODEL = getattr(settings, 'IMAGESTORE_IMAGE_MODEL', None)
if not IMAGE_MODEL:
    admin.site.register(Image, ImageAdmin)

ALBUM_MODEL = getattr(settings, 'IMAGESTORE_ALBUM_MODEL', None)
if not ALBUM_MODEL:
    admin.site.register(AlbumUpload, AlbumUploadAdmin)
