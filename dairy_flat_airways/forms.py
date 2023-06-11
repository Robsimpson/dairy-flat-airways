from django import forms
from datetime import datetime
from zoneinfo import ZoneInfo

from django.forms import DateTimeInput

from .models import Airport, Route


class SearchFlightsForm(forms.Form):
    origin = forms.ChoiceField(label="From", required=False, initial="Surprise Me!", choices=[])
    destination = forms.ChoiceField(label="To", required=False, initial="Surprise Me!", choices=[])
    departure_date = forms.DateTimeField(label="Leave After", initial=datetime.now(), required=False,
                                         widget=DateTimeInput(attrs={'type': 'datetime-local'}))
    return_date = forms.DateTimeField(label="Return By", required=False,
                                      widget=DateTimeInput(attrs={'type': 'datetime-local'}))
    number_of_passengers = forms.IntegerField(label="Passengers", min_value=1, max_value=10,
                                              required=True, initial=1)
    return_required = forms.BooleanField(label="Return", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        valid_airports = [('Surprise Me!', 'Surprise Me!')]
        airports = Airport.objects.all()
        for airport in airports:
            valid_airports.append((airport.id, airport.name))
        # now to ensure the airport actually appears on a route that is active

        current_airports = []
        for route in Route.objects.all():
            for leg in route.routeleg_set.all():
                current_airports.append((leg.origin.id, leg.origin.name))
        current_airports.append(('Surprise Me!', 'Surprise Me!'))

        valid_airports = [item for item in valid_airports if item in current_airports]

        self.fields['origin'].choices = valid_airports
        if not self.fields['origin'].initial:
            self.fields['destination'].choices = valid_airports.remove(self.fields['origin'])
        else:
            self.fields['destination'].choices = valid_airports


class UserDetailsForm(forms.Form):
    email = forms.EmailField(label="Email", required=True)
    first_name = forms.CharField(label="First Name", required=True)
    last_name = forms.CharField(label="Last Name", required=True)
