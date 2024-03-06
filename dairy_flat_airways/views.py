import json
import random

from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render, redirect
from utilities.simulation import update_flight_status, where_are_my_planes
from utilities.scheduling import get_scheduled_flights, get_segments
import urllib.parse

from zoneinfo import ZoneInfo
from datetime import datetime

# Create your views here.
from .models import Schedule, FlightStatus, Airport, RouteLeg, Flight, Ticket, TicketStatus, Plane

from .forms import SearchFlightsForm


def index(request):
    search_flights_form = SearchFlightsForm()

    context = {
        'form': search_flights_form
    }
    return render(request, 'index.html', context)


def about(request):
    airports = Airport.objects.all()
    planes = Plane.objects.all()
    context = {
        'airports': airports,
        'planes': planes
    }

    return render(request, 'about.html', context)


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
                origin = fill_surprise_airport(destination)
            else:
                origin = Airport.objects.get(pk=origin)

            if destination == 'Surprise Me!':
                destination = fill_surprise_airport(origin)
            else:
                destination = Airport.objects.get(pk=destination)

            # calculate the segments required to get between complex routes
            # if none is passed in don't attempt multiple segments, and NZNE cannot by definition have multiple segments
            # as it is the hub, however I will just return a single segment back for that so the
            # function behaviour is general

            segments = get_segments(origin, destination)
            return_unique_list(segments)

            return_segments = []
            if return_required:
                return_segments = get_segments(destination, origin)
                return_unique_list(return_segments)

            timezone = ZoneInfo('Pacific/Auckland')

            scheduled_outbound = []
            # get scheduled flights for each segment
            _return_departure_date = 0
            temp = []
            for option in segments:
                _departure_date = departure_date
                for segment in option:
                    temp = get_scheduled_flights(start_date=_departure_date, end_date=return_date, origin=segment[0],
                                                 destination=segment[1],
                                                 status_inclusions=(FlightStatus.SCHEDULED, FlightStatus.DELAYED),
                                                 excluded_full_flights=True)
                    _departure_date = datetime.fromtimestamp(temp[0].route_details[-1][-1]).astimezone(timezone)
                    scheduled_outbound += temp
                if _return_departure_date == 0:
                    _return_departure_date = _departure_date
                    # this sets the departure date to the date the first optional flight has possibly landed.

            scheduled_return = []
            if return_required:
                for return_option in return_segments:
                    for return_segment in return_option:
                        temp = get_scheduled_flights(start_date=_return_departure_date, end_date=return_date,
                                                     origin=return_segment[0], destination=return_segment[1],
                                                     status_inclusions=(
                                                         FlightStatus.SCHEDULED, FlightStatus.DELAYED),
                                                     excluded_full_flights=True)
                        _return_departure_date = datetime.fromtimestamp(temp[0].route_details[-1][-1]).astimezone(
                            timezone)
                        scheduled_return += temp

            search_flights_form = SearchFlightsForm()

            scheduled_outbound.sort(key=lambda x: x.route_details[0][1])
            scheduled_return.sort(key=lambda x: x.route_details[0][1])

            context = {
                'form': search_flights_form,
                'scheduled_outbound': scheduled_outbound,
                'scheduled_return': scheduled_return,
                'return_checked': return_required,
                'origin': origin,
                'destination': destination,
                'departure_date': departure_date,
                'return_date': return_date,
                'number_of_passengers': number_of_passengers,
                'return_required': return_required,
                'outbound_segments': segments,
                'return_segments': return_segments,
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


def return_unique_list(my_list):
    seen = set()
    for sublist in my_list:
        sublist[:] = [item for item in sublist if item not in seen and not seen.add(item)]


def fill_surprise_airport(existing_airport='Surprise Me!'):
    if existing_airport == 'Surprise Me!':
        all_airports = Airport.objects.all()
    else:
        all_airports = Airport.objects.exclude(id=existing_airport.id)
    return random.sample(list(all_airports), 1)[0]


def book_flights(request):
    print(json.loads(request.body))

    temp_dict = json.loads(request.body)

    outbound_flight = []
    return_flight = []

    for key, value in temp_dict.items():
        working = temp_dict[key]
        temp_leg = [Flight.objects.get(id=working['flight']), working['leg'], working['price']]
        if working['direction'] == 'outbound_flight':
            outbound_flight.append(temp_leg)
        else:
            return_flight.append(temp_leg)

    context = {
        'outbound_flight': outbound_flight,
        'return_flight': return_flight,
        'passengers': working['passengers'],
    }

    return render(request, 'your_ticket.html', context)


def create_bookings(request):

    request_body = json.loads(request.body)

    # create the booking
    for leg in request_body['outbound']:

        ticket = Ticket()

        ticket.first_name = request_body['first_name']
        ticket.last_name = request_body['surname']
        ticket.passengers = request_body['passengers']
        ticket.email = request_body['email']

        ticket.flight_number = leg[0].flight_number

        ticket.status = TicketStatus.SCHEDULED
