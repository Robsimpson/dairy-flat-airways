from datetime import datetime
from dairy_flat_airways.models import Schedule, Flight, FlightStatus
from django.db.models import Q


# I learned something obvious today, lists are passed by reference and remain mutable. Therefore the above
# is passed as a tuple, as they are not mutable - this stopped intelliJ screaming at me in yellow highlights..

def get_scheduled_flights(start_date=datetime.now(), end_date=None, origin=None, destination=None,
                          status_inclusions=None, limit=None):
    # get all the flights within the provided parameters and return as a list, for any specified as none
    # ignore the filter. The filter is dynamically built. The business rule is that flights can be purchased
    # right up until the point they 'Go to gate' (half an hour prior to flight). Passport control is pretty
    # quick in a field.
    if start_date is None:
        start_date = datetime.now()

    filters = Q()
    if start_date is not None:
        filters &= Q(etd_origin__gte=start_date)
    if end_date is not None:
        filters &= Q(etd_origin__lte=end_date)
    if origin is not None:
        filters &= Q(origin=origin)
    if destination is not None:
        filters &= Q(destination=destination)
    if status_inclusions is not None:
        filters &= Q(status__in=status_inclusions)

    scheduled_flights = Flight.objects.filter(filters).order_by('etd_origin')
    if limit:
        scheduled_flights = scheduled_flights[:int(limit)]

    return scheduled_flights
