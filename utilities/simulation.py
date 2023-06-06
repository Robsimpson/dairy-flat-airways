from dairy_flat_airways.models import *
from tqdm import tqdm


def update_flight_status():
    flights = Flight.objects.exclude(status__in=[FlightStatus.COMPLETED, FlightStatus.CANCELLED])
    for f in tqdm(flights):
        f.update_flight()

# calculate flight position
# calculate arc

