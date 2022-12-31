from django import template
from django.shortcuts import get_object_or_404

from ..models import LuggageBill, Trip

register = template.Library()

@register.inclusion_tag('luggages/trip_luggages.html')
def display_trip_luggages(trip_id):
    """ Display the luggages attached to this trip in the admin change_form view. """
    trip = get_object_or_404(Trip, id=trip_id)
    luggages = LuggageBill.objects.filter(trip=trip)
    return {'luggages': luggages, 'trip': trip}
