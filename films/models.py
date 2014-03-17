from django.db import models
from pygeocoder import Geocoder
from django.forms.models import model_to_dict

class FilmLocation(models.Model):
    address = models.CharField(max_length=200, unique=True)
    lat = models.FloatField(blank=True)
    lng = models.FloatField(blank=True)

    class Meta:
        verbose_name_plural = "Film Locations"

    def __unicode__(self):
        return self.address

    def __str__(self):
        return self.address

    def save(self, *args, **kwargs):
        #Geocode the address
        results = Geocoder.geocode(self.address+", San Francisco, CA")
        self.lat = results[0].coordinates[0]
        self.lng = results[0].coordinates[1]
        super(FilmLocation, self).save(*args, **kwargs)

class Film(models.Model):
    title = models.CharField(max_length=200, unique=True)
    release_year = models.PositiveSmallIntegerField('Release Year')
    locations = models.ManyToManyField(FilmLocation)
    fun_facts = models.CharField('Fun Facts', max_length=200, null=True, blank=True)
    production_company = models.CharField('Production Company', max_length=200)
    distributor = models.CharField(max_length=200, null=True, blank=True)
    director = models.CharField(max_length=200)
    writer = models.CharField(max_length=200, null=True, blank=True)
    actors = models.CharField(max_length=200)

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title

    def to_dict(self):
        film_dict = model_to_dict(self)
        film_dict['film_locations'] = []
        for film_location in self.locations.all():
            film_dict['film_locations'].append(model_to_dict(film_location))
        return film_dict