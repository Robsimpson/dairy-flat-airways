import json

from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render, redirect
from utilities.simulation import update_flight_status, where_are_my_planes
from utilities.scheduling import get_scheduled_flights, get_segments
import urllib.parse

from zoneinfo import ZoneInfo

# Create your views here.
from .models import Schedule, FlightStatus, Airport, Route, RouteLeg

from .forms import SearchFlightsForm


def index(request):
    search_flights_form = SearchFlightsForm()

    context = {
        'form': search_flights_form
    }
    return render(request, 'index.html', context)


# ticketing

# my user

# about


# ADMIN FUNCTIONS - schedules, creates schedules, updates flight status to simulate the passage of time.

def seed(request):
    my_schedules = Schedule.objects.all()
    for schedule in my_schedules:
        schedule.create_flights()
    update_flight_status()
    return redirect('/dfairways/')


# APIs that return JSON

# API that returns a list of all flights
def get_scheduled_flight_json(request):
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    origin = request.GET.get('origin', None)
    destination = request.GET.get('destination', None)
    status_inclusions = request.GET.get('status_inclusions', None)
    limit = request.GET.get('limit', None)

    if status_inclusions is None:
        status_inclusions = (FlightStatus.SCHEDULED, FlightStatus.DELAYED)
    else:
        temp_list = []
        for inclusion in status_inclusions.split(','):
            temp_list.append(urllib.parse.unquote(inclusion))
        status_inclusions = tuple(temp_list)  # turn the list into a tuple

    # if datetimes are not passed in in ISO format, it will return as GMT!
    queryset = get_scheduled_flights(start_date, end_date, origin, destination, status_inclusions, limit)
    json_return = serializers.serialize('json', queryset)
    return HttpResponse(json_return, content_type='application/json')


def search_scheduled_flights(request):
    if request.method == 'POST':

        form = SearchFlightsForm(request.POST)

        if form.is_valid():

            origin = form.cleaned_data['origin']
            destination = form.cleaned_data['destination']
            departure_date = form.cleaned_data['departure_date']
            return_date = form.cleaned_data['return_date']
            number_of_passengers = form.cleaned_data['number_of_passengers']
            return_required = form.cleaned_data['return_required']

            if origin == 'Surprise Me!':
                origin = None
            else:
                origin = Airport.objects.get(pk=origin)

            if destination == 'Surprise Me!':
                destination = None
            else:
                destination = Airport.objects.get(pk=destination)

            # calculate the segments required to get between complex routes
            # if none is passed in don't attempt multiple segments, and NZNE cannot by definition have multiple segments
            # as it is the hub, however I will just return a single segment back for that so the
            # function behaviour is general

            if origin is not None and destination is not None:
                segments = get_segments(origin, destination)

            scheduled_flights = get_scheduled_flights(start_date=departure_date, origin=origin, destination=destination)

            search_flights_form = SearchFlightsForm()

            context = {
                'form': search_flights_form,
                'scheduled_flights': scheduled_flights
            }
            # return the flights
            return render(request, 'search_flights.html', context)

        else:
            pass


def get_airport_json(request):
    airports = Airport.objects.all()
    json_return = serializers.serialize('json', airports)
    return HttpResponse(json_return, content_type='application/json')


def get_active_schedule_json(request):
    route_legs = RouteLeg.objects.filter(route_id__schedule__enabled=True)
    json_return = serializers.serialize('json', route_legs)
    return HttpResponse(json_return, content_type='application/json')


def get_aircraft_locations(request):
    plane_locations = where_are_my_planes()
    json_return = json.dumps(plane_locations)
    return HttpResponse(json_return, content_type='application/json')


def trigger_update_flight_status(request):
    update_flight_status()
    return HttpResponse('Flight status updated')
