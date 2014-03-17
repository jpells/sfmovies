from django.test import TestCase, Client
from django.core import management
from films.models import Film, FilmLocation
import json

class ImportTestCase(TestCase):
    def test_import(self):
        management.call_command('import_film_locations', import_file='films/data/test.json')
        self.assertEqual(Film.objects.count(), 2)
        self.assertEqual(FilmLocation.objects.count(), 7)

class FilmTestCase(TestCase):
    def setUp(self):
        film_with_location = Film.objects.create(title="Test", release_year="2014", fun_facts="This is just a test film", production_company="SF Movies Test", distributor="SF Movies Test", director="James Pells", writer="James Pells", actors="James Pells")
        filmlocation = film_with_location.locations.create(address="161 Cleo Rand Ln")
        film_without_location = Film.objects.create(title="Test2", release_year="2014", fun_facts="This is just a test film", production_company="SF Movies Test", distributor="SF Movies Test", director="James Pells", writer="James Pells", actors="James Pells")

    def test_film_to_dict(self):
        film = Film.objects.get(title="Test")
        film_dict = film.to_dict()
        self.assertEqual(film_dict['title'], film.title)
        self.assertEqual(film_dict['release_year'], film.release_year)
        self.assertEqual(film_dict['fun_facts'], film.fun_facts)
        self.assertEqual(film_dict['production_company'], film.production_company)
        self.assertEqual(film_dict['distributor'], film.distributor)
        self.assertEqual(film_dict['director'], film.director)
        self.assertEqual(film_dict['writer'], film.writer)
        self.assertEqual(film_dict['actors'], film.actors)
        filmlocations_dict = film_dict['film_locations']
        self.assertEqual(filmlocations_dict[0]['address'], "161 Cleo Rand Ln")

    def test_has_filmlocations(self):
        film_with_location = Film.objects.get(title="Test")
        film_without_location = Film.objects.get(title="Test2")
        self.assertTrue(film_with_location.locations.count())
        self.assertFalse(film_without_location.locations.count())

    def test_film_location_geocode(self):
        film_with_location = Film.objects.get(title="Test")
        filmlocation = film_with_location.locations.all()[0]
        self.assertEqual(filmlocation.lat, 37.729703)
        self.assertEqual(filmlocation.lng, -122.372124)

    def test_films_view(self):
        c = Client()
        response = c.get('/films/')
        self.assertEqual(response.status_code, 200)
        json_content = json.loads(response.content)
        #Only 1 film has a location
        self.assertEqual(len(json_content['results']), 1)
        self.assertEqual(json_content['results'][0]['title'], 'Test')

    def test_films_title_view(self):
        c = Client()
        response = c.get('/films/?title=Test')
        self.assertEqual(response.status_code, 200)
        json_content = json.loads(response.content)
        self.assertEqual(len(json_content['results']), 1)
        self.assertEqual(json_content['results'][0]['title'], 'Test')

    def test_films_query_view(self):
        #Build search index first
        management.call_command('rebuild_index')
        c = Client()
        response = c.get('/films/?query=tes')
        self.assertEqual(response.status_code, 200)
        json_content = json.loads(response.content)
        #Only 1 film has a location
        self.assertEqual(len(json_content['results']), 1)
        self.assertEqual(json_content['results'][0]['title'], 'Test')