from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from .forms import FileFieldForm


# Create your views here.
class Index(FormView):
    form_class = FileFieldForm
    template_name = "index.html"
    success_url = '/'

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        # files = request.FILES.getlist('file_field')
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)