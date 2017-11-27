from main.models import Organization, Category, Content
from django.contrib.postgres.search import SearchVector

def run():
	vector = SearchVector('title', 'description', 'keywords', 'full_text')
	Content.objects.update(search_vector=vector)

