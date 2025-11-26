from django.urls import path, include
from einsingen.api import api

urlpatterns = [path("api/", api.urls)]
