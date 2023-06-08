from dairy_flat_airways.models import *
from tqdm import tqdm
import re


def update_flight_status():
    flights = Flight.objects.exclude(status__in=[FlightStatus.COMPLETED, FlightStatus.CANCELLED])
    for f in tqdm(flights):
        f.update_flight()


def where_are_my_planes():
    flights = Flight.objects.filter(
        status__in=[FlightStatus.COMPLETED, FlightStatus.IN_FLIGHT, FlightStatus.ATLAYOVER, FlightStatus.DIVERTED],
        etd_origin__lte=datetime.now())
    planes = Plane.objects.all()
    plane_locations = {}
    get_code = re.compile(r'\((.*?)\)')
    right_now = datetime.now().timestamp()
    for plane in planes:
        # get the last flight the plane was involved with, this tells me where it actually is
        last_flight = flights.filter(plane=plane).latest('etd_origin')
        last_flight.update_flight()
        # provide the leg that is current, and then the status will tell the JS what to do with it

        if len(last_flight.route_details) == 1:
            leg = last_flight.route_details[0]
            plane_locations[plane.pk] = {
                'origin': re.search(get_code, leg[0]).group(1),
                'etd_origin': leg[1],
                'destination': re.search(get_code, leg[2]).group(1),
                'etd_destination': leg[3],
                'progress': min(1, (right_now - leg[1]) / (leg[3] - leg[1])),
                'status': last_flight.status.value,
            }
        else:
            # crawl through the legs to find the current one.
            # join the lists together
            legs = []
            for leg in last_flight.route_details:
                legs += leg
            # read backwards through the times until we find where we are
            i = len(legs) - 1
            while i >= 0:
                if right_now > legs[i]:
                    # the flight be stopped somewhere
                    plane_locations[plane.pk] = {
                        'origin': re.search(get_code, legs[i - 3]).group(1),
                        'etd_origin': legs[i - 2],
                        'destination': re.search(get_code, legs[i - 1]).group(1),
                        'etd_destination': legs[i],
                        'progress': 1,
                        'status': last_flight.status.value,
                    }
                    break
                i -= 2
                if right_now > legs[i]:
                    # the flight must be in progress in this leg
                    plane_locations[plane.pk] = {
                        'origin': re.search(get_code, legs[i - 1]).group(1),
                        'etd_origin': legs[i],
                        'destination': re.search(get_code, legs[i + 1]).group(1),
                        'etd_destination': legs[i + 2],
                        'progress': min(1, (right_now - legs[i]) / (legs[i + 2] - legs[i])),
                        'status': last_flight.status.value,
                    }
                    break
                i -= 2

    # return the dict, the view will then handle the JSONifictaion.

    return plane_locations
#
