from datetime import datetime
from dairy_flat_airways.models import Schedule, Flight, FlightStatus, Route
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


def get_segments(origin, destination):
    # build a graph to help find routes
    route_graph = {}
    for route in Route.objects.all():
        for leg in route.routeleg_set.all():
            if leg.origin not in route_graph:
                route_graph[leg.origin] = []
            route_graph[leg.origin].append(leg.destination)

    # find the shortest path between the origin and destination using a breadth first search
    possible_routes = find_routes(route_graph, origin, destination)

    segments = []
    # convert to searchable segments
    for option in possible_routes:
        temp_list = []
        for i in range(0, len(option) - 1):
            temp_list.append((option[i], option[i+ 1]))
        segments.append(temp_list)
    return segments


def find_routes(graph, origin, destination, path=[]):
    path = path + [origin]

    if origin == destination:
        return [path]

    if origin not in graph:
        return []

    routes = []
    for node in graph[origin]:
        if node not in path:
            newpath = find_routes(graph, node, destination, path)
            routes.extend(newpath)

    return routes
