from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render, redirect
from utilities.simulation import update_flight_status
from utilities.scheduling import get_scheduled_flights

from zoneinfo import ZoneInfo

# Create your views here.
from .models import Schedule, FlightStatus


def index(request):
    return render(request, 'index.html')


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

    # if datetimes are not passed in in ISO format, it will return as GMT!
    queryset = get_scheduled_flights(start_date, end_date, origin, destination, status_inclusions, limit)
    json_return = serializers.serialize('json', queryset)
    return HttpResponse(json_return, content_type='application/json')
