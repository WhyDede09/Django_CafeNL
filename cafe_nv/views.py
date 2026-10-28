from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView
from cafe_nv.models import Person

class PersonListView(ListView):
    model = Person
    template_name = "cafe_nv/person_list.html"
    context_object_name = "people"
    paginate_by = 10
