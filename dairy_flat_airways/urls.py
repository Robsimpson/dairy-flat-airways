from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('seed/', views.seed, name='seed'),
    path('about/', views.about, name='about'),
    path('get_scheduled_flight_json/', views.get_scheduled_flight_json, name='get_scheduled_flight_json'),
    path('search_scheduled_flights/', views.search_scheduled_flights, name='search_scheduled_flights'),
    path('get_airport_json/', views.get_airport_json, name='get_airport_json'),
    path('get_active_schedule_json/', views.get_active_schedule_json, name='get_active_schedule_json'),
    path('get_aircraft_locations/', views.get_aircraft_locations, name='get_active_schedule_json'),
    path('trigger_update_flight_status/', views.trigger_update_flight_status, name='trigger_update_flight_status'),
    path('book_flights/', views.book_flights, name='book_flights'),
    path('create_bookings/', views.create_bookings, name='create_booking'),
]

