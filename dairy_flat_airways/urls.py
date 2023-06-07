from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('seed/', views.seed, name='seed'),
    path('get_scheduled_flight_json/', views.get_scheduled_flight_json, name='get_scheduled_flight_json'),
    path('search_scheduled_flights/', views.search_scheduled_flights, name='search_scheduled_flights'),
]

