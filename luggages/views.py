from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render

from .models import Customer, LuggageBill, Trip, Weight


def homepage(request):
    weights = Weight.objects.all()

    template_name = "luggages/home.html"
    context = {
        "weights": weights,
    }

    return render(request, template_name, context)


@staff_member_required
def admin_luggagebill_detail(request, luggagebill_id):
    luggagebill = get_object_or_404(LuggageBill, id=luggagebill_id)

    template_name = "admin/luggages/luggagebill/detail.html"
    context = {
        "luggagebill": luggagebill,
    }

    return render(request, template_name, context)


@staff_member_required
def admin_customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    luggage_bills = customer.luggagebill_set.all()

    template_name = "admin/luggages/customer/detail.html"
    context = {
        "customer": customer,
        "luggage_bills": luggage_bills,
    }

    return render(request, template_name, context)


@staff_member_required
def admin_trip_luggages(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    luggages = LuggageBill.objects.filter(trip=trip)

    template_name = "admin/luggages/trip/detail.html"
    context = {
        "trip": trip,
        "luggages": luggages,
    }

    return render(request, template_name, context)
