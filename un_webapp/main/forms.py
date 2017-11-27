from django import forms
from django.contrib.auth import get_user_model

from registration.forms import RegistrationForm

from .models import Query, Content, Organization
from datetime import datetime

User = get_user_model()
MIN_YEAR = 2011
MAX_YEAR = datetime.now().year

class QueryForm(forms.ModelForm):
    # country = forms.ChoiceField(choices=((x, x) for x in Content.objects.get_countries_list()), initial="All countries"	)
    year = forms.ChoiceField(choices=[('All years', 0)] + [(str(year), year) for year in range(MIN_YEAR, MAX_YEAR+1)], initial=0)
    # organization = forms.ChoiceField(choices=[('All organizations', 'All organizations')] + [(org.name, org.name) for org in Organization.objects.all()], initial="All organizations")
    
    class Meta:
        model = Query
        fields = ('text', 'offer', 'request', 'publication', 'country', 'year', 'organization')

    def __init__(self, *args, **kwargs):
    	super(QueryForm, self).__init__(*args, **kwargs)
    	self.fields['country'] = forms.ChoiceField(choices=((x, x) for x in Content.objects.get_countries_list()), initial="All countries")
    	self.fields['organization'] = forms.ChoiceField(choices=[('All organizations', 'All organizations')] + [(org.name, org.name) for org in Organization.objects.all()], initial="All organizations")



class ExtendedUserCreationForm(RegistrationForm):

    email = forms.EmailField(label="Email")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2",)
