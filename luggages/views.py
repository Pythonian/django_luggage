from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required

from .models import LuggageBill, Customer, Trip, Luggage


@staff_member_required
def admin_luggagebill_detail(request, luggagebill_id):
    luggagebill = get_object_or_404(LuggageBill, id=luggagebill_id)
    return render(request, 'admin/luggages/luggagebill/detail.html', {'luggagebill': luggagebill})


@staff_member_required
def admin_customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    return render(request, 'admin/luggages/customer/detail.html', {'customer': customer})


@staff_member_required
def admin_trip_luggages(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    luggages = LuggageBill.objects.filter(trip=trip)
    return render(request, 'admin/luggages/trip/detail.html', {'trip': trip, 'luggages': luggages})
