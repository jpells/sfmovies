from django.http import HttpResponse
from django.views.generic import TemplateView
from django.conf import settings
from films.models import Film
from haystack.query import SearchQuerySet
import simplejson as json

class IndexTemplateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(IndexTemplateView, self).get_context_data(**kwargs)
        context['GOOGLE_MAPS_API_KEY'] = settings.GOOGLE_MAPS_API_KEY
        return context

class FilmsJsonView(TemplateView):
    """
    This can be used by other services to get films and their locations via json.

    Parameters:
        ?query -- Returns films who's title/director/actors contain the query
        ?title -- Returns the film who's title is an exact match

    Return:
        JSON String --  {"results":
                            [{"release_year": RELEASE_YEAR,
                            "title": TITLE,
                            "film_locations":
                                [{"lat": LAT, "lng": LNG, "id": FILMLOCATION_ID, "address": ADDRESS},],
                            "fun_facts": FUN_FACTS,
                            "writer": WRITER,
                            "locations": [FILMLOCATION_ID,],
                            "director": DIRECTOR,
                            "production_company": PRODUCTION_COMPANY,
                            "actors": ACTORS,
                            "distributor": DISTRIBUTOR,
                            "id": FILM_ID},]
                        }
    """
    def render_to_response(self, context, **response_kwargs):
        films_dict = []
        if self.request.GET.get('query'):
            #Retrieve films from the autocomplete search using the query
            sqs = SearchQuerySet().autocomplete(text=self.request.GET.get('query', ''))
            for result in sqs:
                if result.object.locations.count():
                    films_dict.append(result.object.to_dict())
        elif self.request.GET.get('title'):
            #Retrieve film by title
            film = Film.objects.get(title=self.request.GET.get('title'))
            films_dict.append(film.to_dict())
        else:
            #Retrieve all films
            films = Film.objects.all()
            for film in films:
                if film.locations.count():
                    films_dict.append(film.to_dict())
        the_data = json.dumps({
            'results': films_dict
        })
        return HttpResponse(the_data, content_type='application/json')