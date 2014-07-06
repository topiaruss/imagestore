from django.core.management.base import BaseCommand, CommandError
from imagestore.models.image import Image
from sorl.thumbnail import get_thumbnail
import time

class Command(BaseCommand):
    args = '<thumbspec thumbspec ...>'
    help = 'checks that all thumbspecs are available for all images'

    def handle(self, *args, **options):

        started = time.time()

        high_water_mark = None

        specs = args if args else ('688x312', '120x85', '290x260', '590x263', '166x213',
                                   '276x196', '150x150', '120x120', '600x600', '241', 'x470')
        specs = sorted(set(specs))

        if not args:
            self.stdout.write('No specs given. Processing these default specs, center cropped, at q=95% (default).')
            self.stdout.write('')
            for spec in specs:
                self.stdout.write('  %s' % spec)
            self.stdout.write('')

        def slice():
            if time.time() > (started + (60*60)):
                self.stdout.write('Allotted time has elapsed. Bye')
                import sys
                sys.exit()

        def process_images(images):
            "we process images in random order, to avoid lockstep"
            images=images.order_by('?')
            for im in images:
                self.stdout.write('creating for %s' % im.image.name)
                start_image = time.time()
                for spec in specs:
                    start_thumb = time.time()
                    tn = get_thumbnail(im.image, spec, crop='center')
                    thumbtime = time.time() - start_thumb
                    self.stdout.write('%s:%.2f ' % (spec, thumbtime), ending='')
                self.stdout.write('')
                imagetime = time.time() - start_image
                self.stdout.write('image time: %.2f' % imagetime)
                self.stdout.write('')
                slice()

        while 1:
            images = Image.objects.all().order_by('-pk')
            if images.count():
                current_top = images[:1].get().pk
                if high_water_mark != current_top:
                    process_images(images)
                    high_water_mark = current_top
            time.sleep(60)
            slice()


