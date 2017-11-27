from django.shortcuts import render, redirect
from django.views.generic import TemplateView, DetailView
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta
from django.forms.models import model_to_dict
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import datetime
import urllib

from .forms import QueryForm
from .models import Query, Content

from ipware.ip import get_real_ip

class BaseSCTView(TemplateView):
    #check for user in get requests for header
    def get_context_data(self, **kwargs):
        context = super(BaseSCTView, self).get_context_data(**kwargs)
        try:
            user = self.request.user
        except:
            user = None #try except for unit tests, which don't create users for WSGI req.
        context['user'] = user if user else AnonymousUser()
        return context

    def determine_session(self):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
            self.request.session.model.objects.filter(session_key=self.request.session.session_key).update(session_data={'ip_address': get_real_ip(self.request)})
        return self.request.session

class IndexView(BaseSCTView):
    '''index view'''

    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        req_dict = self.request.__dict__
        context['query'] = QueryForm()
        return context


class SearchResults(BaseSCTView):
    '''Combined view. POST requests create queries, GET requests return content.'''

    template_name = 'main/search_results.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(SearchResults, self).get_context_data(**kwargs)
        query_id = self.request.GET.get('id', None)
    
        results = Content.objects.exec_query(query_id)
        context['query'] = QueryForm(model_to_dict(Query.objects.get(pk=query_id)))
        context['query_id'] = query_id
        

        paginator = Paginator(results, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            results_page = paginator.page(page)
        except PageNotAnInteger:
            results_page = paginator.page(1)
        except EmptyPage:
            results_page = paginator.page(paginator.num_pages)
        context['results'] = results_page
        context['advanced'] = True
        return context

    def post(self, request, *args, **kwargs):
        # TODO: take request+params and save searches
        # query = urlparse.parse_qs(urlparse.urlsplit(request.data).query)
        req = True if request.POST.get('request', None) == 'on' else False
        offer = True if request.POST.get('offer', None) == 'on' else False
        publication = True if request.POST.get('publication', None) == 'on' else False
        year = request.POST.get('year', None)
        country = request.POST.get('country', None)
        organization = request.POST.get('organization', None)
        session = self.determine_session()
        q = Query.objects.get_or_create(text=request.POST['text'],
                  request=req,
                  offer=offer,
                  publication=publication,
                  country=country,
                  year=year,
                  organization=organization,
                  session_key=session.session_key)[0] #prevent double results

        user = request.user
        if not isinstance(user, AnonymousUser):
            q.user = user

        q.save()
        query_string = urllib.parse.urlencode(
            model_to_dict(q, fields=['text', 'offer', 
                                     'request', 'publication','id', 'year', 'country', 'organization']))

        return redirect('/search/results?' + query_string)

    def get(self, request, *args, **kwargs):
        #filter based on args in url
        return super(SearchResults, self).get(request, *args, **kwargs)

class SearchDetail(DetailView, BaseSCTView):

    template_name = 'main/detail.html'
    #prob put a redirect in the dispatch if no signed in user
    model = Content
    slug_field = 'content_id'

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super(SearchDetail, self).get_context_data(**kwargs)
        context['organization'] = self.object.organization.name
        return context

class UserProfile(BaseSCTView):
    template_name = 'main/profile.html'

    def get_context_data(self, **kwargs):
        context = super(UserProfile, self).get_context_data(**kwargs)
        if not isinstance(context['user'], AnonymousUser):
            context['searches'] = Query.objects.filter(user=context['user'])
            context['saved_content'] = Content.objects.filter(users=context['user']).all()
        else:
            context['searches'] = Query.objects.filter(session_key=self.determine_session().session_key)
        return context

def save_content(request):
    try:
        user = User.objects.get(id=request.GET.get('user'))
        content = Content.objects.get(id=request.GET.get('content'))
        content.users.add(user)
        response = {'message': 'Content saved.'}
    except:
        response = {'message': 'Error occurred when saving content.'}
    return JsonResponse(response, content_type="application/json")

