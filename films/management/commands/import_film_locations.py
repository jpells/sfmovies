from django.core.management.base import BaseCommand
from django.conf import settings
from films.models import Film, FilmLocation
from pygeocoder import GeocoderError
from optparse import make_option
import urllib2
import simplejson
import logging
import os

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--import_file',
            dest='import_file',
            default=None,
            help='Use specified import file.'),
        )
    help = 'Imports Film Locations'

    def handle(self, *args, **options):
        self.stdout.write('Importing Film Locations')
        logger = logging.getLogger(__name__)
        #Get film location data
        if options.get('import_file'):
            f = open(os.path.join(settings.BASE_DIR, options.get('import_file')), 'r')
        else:
            req = urllib2.Request(settings.SF_FILM_LOCATION_DATA_URL)
            opener = urllib2.build_opener()
            f = opener.open(req)
        film_data = simplejson.load(f)
        film_counter = 0
        filmlocation_counter = 0
        filmlocation_skipped_counter = 0
        filmlocation_reused_counter = 0
        for film_row in film_data:
            logger.info('Importing Film: '+film_row['title'])
            if film_row.get('locations'):
                #Normalize data by stripping whitespace from beginning and end of column values
                for column in film_row:
                    film_row[column] = film_row[column].lstrip().rstrip()
                try:
                    #Check if film already exists
                    film = Film.objects.get(title=film_row['title'])
                except Film.DoesNotExist:
                    #If film doesn't exist create it
                    actors = [film_row.get('actor_1', ""), film_row.get('actor_2', ""), film_row.get('actor_3', "")]
                    film = Film(title=film_row['title'], release_year=film_row['release_year'], fun_facts=film_row.get('fun_facts', None), production_company=film_row['production_company'], distributor=film_row.get('distributor', None), director=film_row['director'], writer=film_row.get('writer', None), actors=", ".join(actor for actor in actors if actor != ""))
                    film.save()
                    film_counter += 1
                logger.info('Importing Film Location: '+film_row['locations'])
                #Check if film location already exists
                film_locations = film.locations.filter(address=film_row['locations'])
                if not film_locations:
                    #If film location doesn't exist for film check if it exists for any other films
                    film_locations = FilmLocation.objects.filter(address=film_row['locations'])
                    if not film_locations:
                        try:
                            film.locations.create(address=film_row['locations'])
                            filmlocation_counter += 1
                        except GeocoderError:
                            logger.warning('Cannot find coordinates for: '+film_row['locations'])
                            filmlocation_skipped_counter += 1
                    else:
                        film.locations.add(film_locations[0])
                        filmlocation_reused_counter += 1
            else:
                filmlocation_skipped_counter += 1
        self.stdout.write('Imported '+str(film_counter)+' film(s)')
        self.stdout.write('Imported '+str(filmlocation_counter)+' film location(s)')
        self.stdout.write('Skipped '+str(filmlocation_skipped_counter)+' film location(s)')
        self.stdout.write('Reused '+str(filmlocation_reused_counter)+' film location(s)')