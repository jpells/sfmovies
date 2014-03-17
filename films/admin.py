from django.contrib import admin
from films.models import Film, FilmLocation

class FilmAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_year', 'production_company', 'distributor', 'director', 'writer', 'actors')
    filter_horizontal = ('locations',)

class FilmLocationAdmin(admin.ModelAdmin):
    list_display = ('address', 'lat', 'lng')

admin.site.register(Film, FilmAdmin)
admin.site.register(FilmLocation, FilmLocationAdmin)