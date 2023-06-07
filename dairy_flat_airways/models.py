import datetime
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from django.db import models
from django.utils import timezone
from enum import Enum
from enumfields import EnumField


# Create your models here.
class ScheduleType(Enum):
    MON = 0
    TUE = 1
    WED = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6
    WEEKDAY = 7
    WEEKEND = 8
    WEEKLY = 9


class FlightStatus(Enum):
    SCHEDULED = 'Scheduled'
    GO_TO_GATE = 'Go To Gate'
    BOARDED = 'Boarded'
    IN_FLIGHT = 'In Flight'
    COMPLETED = 'Completed'
    CANCELLED = 'Cancelled'
    DELAYED = 'Delayed'
    DIVERTED = 'Diverted'
    UNKNOWN = 'Unknown'
    ATLAYOVER = 'At Layover'


class TicketStatus(Enum):
    SCHEDULED = 'Scheduled'
    IN_FLIGHT = 'In Flight'
    COMPLETED = 'Completed'
    CANCELLED = 'Cancelled'
    TRANSFERRED = 'Transfer'
    UNKNOWN = 'Unknown'


# Users (are users, can buy tickets)
class Users(models.Model):
    id = models.AutoField(primary_key=True)
    email_address = models.EmailField(max_length=254)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    passport_number = models.CharField(max_length=30)
    passport_expiry = models.DateField()
    passport_country = models.CharField(max_length=30)
    passport_issue = models.DateField()
    passport_issue_country = models.CharField(max_length=30)
    passport_issue_city = models.CharField(max_length=30)


# Planes
class Plane(models.Model):
    tail_number = models.CharField(max_length=30, primary_key=True)
    model = models.ForeignKey('PlaneModel', on_delete=models.PROTECT)


class PlaneModel(models.Model):
    id = models.AutoField(primary_key=True)
    model = models.CharField(max_length=30)
    manufacturer = models.CharField(max_length=30)
    capacity = models.IntegerField()
    range = models.IntegerField()
    takeoff_distance = models.IntegerField()
    landing_distance = models.IntegerField()
    max_speed = models.IntegerField()
    eng_desc = models.CharField(max_length=30)
    max_altitude = models.IntegerField()
    description = models.CharField(max_length=254)


# Flights are instantiated routes, with a plane, an ETD and tickets (join a plane, a route, ETA)
# These are 'factory' created from the schedule, but they store their own information to allow
# for future extension of modifying a specific flight, one time, without stuffing the template

class Flight(models.Model):
    YOUR_ENUM_CHOICES = [(tag, tag.value) for tag in FlightStatus]

    id = models.AutoField(primary_key=True)
    flight_number = models.CharField(max_length=30)
    plane = models.ForeignKey('Plane', on_delete=models.PROTECT)
    # if I attach a route here, it can be replaced with a new route, then changed for flexibility as an extension
    # if time allows creating admin interface to modify a specific flight
    route = models.ForeignKey('Route', on_delete=models.PROTECT)
    route_details = models.JSONField(max_length=254)
    etd_origin = models.DateTimeField(null=True)
    stage = models.IntegerField(default=1)
    status = EnumField(FlightStatus, default=FlightStatus.SCHEDULED)

    def update(self, flight_number, plane, route, etd_origin):
        self.flight_number = flight_number
        self.plane = plane
        self.route = route
        self.etd_origin = etd_origin
        self.recalc_route_details()

    def update_route(self, route):
        self.route = route
        self.recalc_route_details()

    def update_etd_origin(self, etd_origin):
        self.etd_origin = etd_origin
        self.recalc_route_details()

    def recalc_route_details(self):
        self.route_details = []
        for leg in self.route.routeleg_set.all():
            temp = [leg.origin.name_and_code()]
            if len(self.route_details) == 0:
                temp.append(self.etd_origin.timestamp())
            else:
                temp.append(
                    self.calculate_turnaround(datetime.fromtimestamp(self.route_details[-1][3]), 2, 15).timestamp())
            temp.append(leg.destination.name_and_code())
            temp.append(self.calculate_eta(leg.distance, temp[1]).timestamp())
            self.route_details.append(temp)

    # calculate the eta for the destination based on the distance and the plane cruise speed
    def calculate_eta(self, distance, start_time):
        return datetime.fromtimestamp(start_time) + timedelta(hours=(distance / self.plane.model.max_speed) + 0.5)

    def calculate_turnaround(self, eta_stop_time, layover_hours, rounding_minutes):
        rounded_time = eta_stop_time.replace(minute=((eta_stop_time.minute // rounding_minutes) * rounding_minutes),
                                             second=0, microsecond=0)
        return rounded_time + timedelta(hours=layover_hours)

    def update_flight(self):
        if self.status in(FlightStatus.SCHEDULED, FlightStatus.DELAYED, FlightStatus.ATLAYOVER):
            # subtracting seconds * minutes from a timestamp looks a little obtuse, -1800 is -30m
            if datetime.now() >= datetime.fromtimestamp(self.route_details[self.stage-1][1] - 1800):
                self.status = FlightStatus.GO_TO_GATE
        # these aren't elifs, essentially so that if this is run with flights WAY in the past it catches
        # up as each if statement will cascade
        if self.status == FlightStatus.GO_TO_GATE:
            if datetime.now() >= datetime.fromtimestamp(self.route_details[self.stage-1][1] - 900):
                self.status = FlightStatus.BOARDED
        if self.status == FlightStatus.BOARDED:
            if datetime.now() >= datetime.fromtimestamp(self.route_details[self.stage-1][1]):
                self.status = FlightStatus.IN_FLIGHT
        if self.status == FlightStatus.IN_FLIGHT:
            if datetime.now() >= datetime.fromtimestamp(self.route_details[self.stage-1][3]):
                if self.stage == len(self.route_details):
                    self.status = FlightStatus.COMPLETED
                else:
                    self.status = FlightStatus.ATLAYOVER
                    self.stage += 1
        self.save()


# Airports (planes depart and arrive at) have a name code and location, a route joins two together. NOTE locations
# have timezones!!
class Airport(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=30)
    location = models.CharField(max_length=30)
    lat = models.FloatField()
    long = models.FloatField()
    timezone = models.CharField(max_length=30)
    description = models.CharField(max_length=254)

    def name_and_code(self):
        return self.name + " (" + self.id + ")"

    def __str__(self):
        return self.name


# Routes define a flight path
class Route(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)


# I don't know why, but Django won't allow me to remove this model!
class RouteToLeg(models.Model):
    # id = models.AutoField(primary_key=True)
    # route = models.ForeignKey(Route, on_delete=models.PROTECT)
    # RouteLeg = models.ForeignKey('RouteLeg', on_delete=models.PROTECT)
    pass


class RouteLeg(models.Model):
    id = models.AutoField(primary_key=True)
    route_id = models.ForeignKey(Route, on_delete=models.PROTECT)
    origin = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name='origin_airport')
    destination = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name='destination_airport')
    distance = models.FloatField()


# Schedules are used as a factory to create flights in the future schedule
class Schedule(models.Model):
    id = models.AutoField(primary_key=True)
    route = models.ForeignKey(Route, on_delete=models.PROTECT)
    aircraft = models.ForeignKey(Plane, on_delete=models.PROTECT)
    schedule = models.CharField(max_length=254)  # This will hold a JSON for schedule creation
    enabled = models.BooleanField(default=True)

    def get_schedules(self):
        temp_list = json.loads(self.schedule)
        for item in temp_list:
            item[0] = ScheduleType[item[0]]
        return temp_list

    def get_flight_number(self):
        return 'DFA-' + str(self.id)

    def create_flights(self, days=60 + 1):
        # Create flights from schedule
        timezone = ZoneInfo('Pacific/Auckland')
        today = datetime.date(datetime.now(timezone))
        schedules = self.get_schedules()

        # this creates backwards in time to demonstrate the status changes
        for day in range(-30, days):
            offset_datetime = today + timedelta(days=day)
            offset_day_number = today.weekday() + day
            for schedule in schedules if self.enabled else []:
                etd_origin = datetime.combine(offset_datetime,
                                              datetime.strptime(schedule[1], '%H%M').time()).astimezone(timezone)
                fn = self.get_flight_number()
                if schedule[0] == ScheduleType.WEEKLY:
                    create_new_flight(fn, self.aircraft, self.route, etd_origin)
                elif schedule[0] == ScheduleType.WEEKDAY:
                    if offset_day_number % 7 in [1, 2, 3, 4, 5]:
                        create_new_flight(fn, self.aircraft, self.route, etd_origin)
                elif schedule[0] == ScheduleType.WEEKEND:
                    if offset_day_number % 7 in [6, 7]:
                        create_new_flight(fn, self.aircraft, self.route, etd_origin)
                elif offset_day_number % 7 == schedule[0].value:
                    create_new_flight(fn, self.aircraft, self.route, etd_origin)


def create_new_flight(fn, aircraft, route, etd_origin):
    if not check_flight_exists(fn, etd_origin):
        new_flight = Flight()
        new_flight.update(fn, aircraft, route, etd_origin)
        new_flight.save()


def check_flight_exists(flight_number, etd_origin):
    # Test the flight doesn't already exist by checking that there are no records with the tail
    # number and the date in the ETD_origin field
    return Flight.objects.filter(flight_number=flight_number, etd_origin=etd_origin).exists()


# Tickets (join a passenger to a flight. Capacity minus tickets = seats available)
class Ticket(models.Model):
    YOUR_ENUM_CHOICES = [(tag, tag.value) for tag in FlightStatus]

    id = models.AutoField(primary_key=True)
    passenger = models.ForeignKey(Users, on_delete=models.PROTECT)
    flight = models.ForeignKey(Flight, on_delete=models.PROTECT)
    seat = models.CharField(max_length=30)
    price = models.IntegerField()
    status = EnumField(TicketStatus, default=TicketStatus.SCHEDULED)
