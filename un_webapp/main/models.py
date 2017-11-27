from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.sessions.models import Session
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank, SearchVectorField
from django.db.models import F, Q
from django.dispatch import receiver
from django.db.models.signals import pre_save
import functools
import operator
import os

class ContentQuerySet(models.QuerySet):

    # offer, request, category are boolean arguments 
    def filter_category(self, offer, request, publication):
        categories = Category.objects.all()
        
        if not offer:
            categories = categories.filter(~Q(name="offer") & ~Q(name="Offer"))
        if not request:
            categories = categories.filter(~Q(name="Need"))
        if not publication:
            categories = categories.filter(~Q(name="Publication"))

        return self.filter(category__id__in=categories.values('id'))

    def filter_year(self, year):
        if year:
            return self.filter(date_published__year=year)
        else:
            return self

    def filter_country(self, country):
        if country == 'All countries':
            return self
        else:
            return self.filter(country=country)

    def filter_organization(self, org_name):
        if org_name == 'All organizations':
            return self
        else:
            return self.filter(organization__name=org_name)

class ContentManager(models.Manager):
    '''Custom manager to insert a bit more customizability in the content search'''

    def get_queryset(self):
        return ContentQuerySet(self.model, using=self._db)

    def search(self, query_dict):
        queryset = self.get_queryset().filter_category(query_dict['offer'], query_dict['request'], query_dict['publication'])
        queryset = queryset.filter_year(query_dict['year']).filter_country(query_dict['country']).filter_organization(query_dict['organization'])

        search_text = query_dict['text']
        # TODO: Remove english stop words
        if not search_text:
            return queryset
        terms = [SearchQuery(term) for term in search_text.split()]
        query_terms = functools.reduce(operator.or_, terms)
        queryset = queryset.annotate(rank=SearchRank(F('search_vector'), query_terms)).filter(search_vector=query_terms).order_by('-rank')

        return queryset.filter(rank__gte=0.04)

    # execute search for exsiting query
    def exec_query(self, query_id):
        query = Query.objects.get(pk=query_id)
        return self.search(query.__dict__)

    # return list of valid countries for filtering
    def get_countries_list(self):
        countries = list(Content.objects.all().order_by('country').values_list('country', flat=True).distinct())
        # filter out '', ' ', and two digit numeric values (not a permanent solution)
        return ['All countries'] + [country for country in countries if len(country) > 2]




class Content(models.Model):
    '''Main search result object.'''
    objects = ContentManager()
    organization = models.ForeignKey('Organization')
    content_type = models.CharField(max_length=255, null=True, blank=True) #probable Choice
    category = models.ForeignKey('Category', default=None, null=True) 
    collected_date = models.DateField()
    title = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True) 
    short_description = models.TextField(null=True, blank=True) #shows up on main results page
    url = models.URLField(max_length=255, null=True, blank=True) #not always avail
    sector = models.CharField(max_length=75) #probable ChoiceField
    country = models.CharField(max_length=255, null=True, blank=True)
    keywords = models.CharField(max_length=1000, null=True, blank=True)
    full_text = models.TextField(null=True, blank=True)
    date_published = models.DateField(null=True, blank=True)
    advantages = models.CharField(max_length=255, null=True, blank=True) # needs to be longer
    contact = models.ForeignKey('Contact', null=True, default=None)
    search_vector = SearchVectorField(null=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.title


class Contact(models.Model):
    '''Contact information for content'''
    name = models.CharField(max_length=255)
    company = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    zip = models.CharField(max_length=20, null=True,blank=True)
    #also possibly store geolocational data here for mapping later

    def __str__(self):
        return self.name

class Query(models.Model):
    '''User search details'''
    text = models.CharField(max_length=255)
    query_time = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    session_key = models.CharField(max_length=255, null=True, blank=True)
    offer = models.BooleanField(default=True)
    request = models.BooleanField(default=True)
    publication = models.BooleanField(default=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    year = models.IntegerField(default=0, null=True, blank=True)
    organization = models.CharField(max_length=100, null=True, blank=True)
    query_string = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.text

class Category(models.Model):
    '''foreign key for content categories'''
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Organization(models.Model):
    '''foreign key for content sources'''
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

@receiver(pre_save, sender=Content)
def generate_short_desc(instance, *args, **kwargs):
    description = instance.description if instance.description else ''
    if len(description.split(' ')) > 50:
        instance.short_description = ' '.join(description.split(' ')[:50]) + "..."
    else:
        instance.short_description = description
