from django.core.management.base import BaseCommand, CommandError
from imagestore.models.image import Image
from sorl.thumbnail import get_thumbnail
import time
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

ALLOTTED_TIME = 60 * 60 # 1 hour

class Command(BaseCommand):
    args = '<thumbspec thumbspec ...>'
    help = 'checks that all thumbspecs are available for all images'

    def log(self, m):
        logger.debug(m)

    def handle(self, *args, **options):

        started = time.time()

        high_water_mark = None

        self.total_processed = self.total_thumbs = self.processed_this_pass = 0

        specs = args if args else settings.AUTO_IMAGE_THUMBNAIL_LIST
        specs = sorted(set(specs))

        if not args:
            self.stdout.write('No specs given. Using the default specs')
        self.stdout.write('Processing the following, center cropped, at q=95%% (default). Up to %s seconds' % ALLOTTED_TIME)
        self.stdout.write('')
        for spec in specs:
            self.stdout.write('  %s' % spec)
        self.stdout.write('')
        self.log('Starting force_thumbnails run, for specs %s' % specs)

        def slice():
            if time.time() > (started + ALLOTTED_TIME):
                self.stdout.write('Allotted time of %s seconds has elapsed. Total Processed: %s, Total Thumbs: %s, Remaining to check %s' %
                         (ALLOTTED_TIME, self.total_processed, self.total_thumbs, self.images_to_check-self.processed_this_pass))
                self.log('Allotted time of %s seconds has elapsed. Total Processed: %s, Total Thumbs: %s, Remaining to check %s' %
                         (ALLOTTED_TIME, self.total_processed, self.total_thumbs, self.images_to_check-self.processed_this_pass))
                import sys
                sys.exit()

        def process_images(images):
            "we process images in random order, to avoid lockstep"
            images=images.order_by('?')
            self.processed_this_pass = 0
            for im in images:
                self.stdout.write('creating for %s' % im.image.name)
                self.log('creating for %s' % im.image.name)
                start_image = time.time()
                accu = 'thumb times: '
                for spec in specs:
                    start_thumb = time.time()
                    tn = get_thumbnail(im.image, spec, crop='center')
                    thumbtime = time.time() - start_thumb
                    self.stdout.write('%s:%.2f ' % (spec, thumbtime), ending='')
                    accu += ('"%s"=%.2f  ' % (spec, thumbtime))
                    self.total_thumbs += 1
                self.stdout.write('')
                imagetime = time.time() - start_image
                self.stdout.write('image time: %.2f' % imagetime)
                self.stdout.write('')
                self.log('image time: %.2f // %s' % (imagetime, accu))
                self.total_processed += 1
                self.processed_this_pass += 1
                slice()

        while 1:
            images = Image.objects.all().order_by('-pk')
            current_top = images[:1].get().pk
            while images.count() and high_water_mark != current_top:
                self.images_to_check = images.count()
                process_images(images)
                high_water_mark = current_top
                # see if more images have come in
                images = Image.objects.all().order_by('-pk')
                current_top = images[:1].get().pk
            time.sleep(60)
            slice()


